"""
Streamer for reading input
"""

# Copyright (C) 2021-2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import abc
import multiprocessing
import os
import queue
import sys
from enum import Enum
from typing import Dict, Iterator, Optional, Union

import cv2
import numpy as np


class InvalidInput(Exception):
    """
    Exception for wrong input format
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class OpenError(Exception):
    """
    Exception for open reader
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class MediaType(Enum):
    """
    This Enum represents the types of input
    """

    IMAGE = 1
    DIR = 2
    VIDEO = 3
    CAMERA = 4


class BaseStreamer(metaclass=abc.ABCMeta):
    """
    Base Streamer interface to implement Image, Video and Camera streamers.
    """

    @abc.abstractmethod
    def __iter__(self) -> Iterator[np.ndarray]:
        """
        Iterate through the streamer object that is a Python Generator object.
        :return: Yield the image or video frame.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_type(self) -> MediaType:
        """
        Get type of streamer
        """
        raise NotImplementedError


def _process_run(streamer: BaseStreamer, buffer: multiprocessing.Queue) -> None:
    """
    Private function that is run by the thread.

    Waits for the buffer to gain space for timeout seconds while it is full.
    If no space was available within this time the function will exit

    :param streamer: The streamer to retrieve frames from
    :param buffer: The buffer to place the retrieved frames in
    """
    for frame in streamer:
        buffer.put(frame)


class ThreadedStreamer(BaseStreamer):
    """
    Runs a BaseStreamer on a seperate thread.

    :param streamer: The streamer to run on a thread
    :param buffer_size: Number of frame to buffer internally

    :example:

        >>> streamer = VideoStreamer(path="../demo.mp4")
        >>> threaded_streamer = ThreadedStreamer(streamer)
        ... for frame in threaded_streamer:
        ...    pass
    """

    def __init__(self, streamer: BaseStreamer, buffer_size: int = 2) -> None:
        self.buffer_size = buffer_size
        self.streamer = streamer

    def __iter__(self) -> Iterator[np.ndarray]:
        buffer: multiprocessing.Queue = multiprocessing.Queue(maxsize=self.buffer_size)
        process = multiprocessing.Process(
            target=_process_run, args=(self.streamer, buffer)
        )
        # Make thread a daemon so that it will exit when the main program exits as well
        process.daemon = True
        process.start()

        try:
            while process.is_alive() or not buffer.empty():
                try:
                    yield buffer.get(timeout=0.1)
                except queue.Empty:
                    pass
        except GeneratorExit:
            process.terminate()
        finally:
            process.join(timeout=0.1)
            # The kill() function is only available in Python 3.7.
            # Skip it if running an older Python version.
            if sys.version_info >= (3, 7) and process.exitcode is None:
                process.kill()

    def get_type(self) -> MediaType:
        """
        Get type of internal streamer
        """
        return self.streamer.get_type()


class VideoStreamer(BaseStreamer):
    """
    Video Streamer
    :param path: Path to the video file.

    :example:

        >>> streamer = VideoStreamer(path="../demo.mp4")
        ... for frame in streamer:
        ...    pass
    """

    def __init__(self, input_path: str, loop: bool) -> None:
        self.media_type = MediaType.VIDEO
        self.loop = loop
        self.cap = cv2.VideoCapture()
        status = self.cap.open(input_path)
        if not status:
            raise InvalidInput(f"Can't open the video from {input_path}")

    def __iter__(self) -> Iterator[np.ndarray]:
        while True:
            status, image = self.cap.read()
            if status:
                yield cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                if self.loop:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                else:
                    break

    def get_type(self) -> MediaType:
        return MediaType.VIDEO


class CameraStreamer(BaseStreamer):
    """
    Stream video frames from camera
    :param camera_device: Camera device index e.g, 0, 1

    :example:

        >>> streamer = CameraStreamer(camera_device=0)
        ... for frame in streamer:
        ...     cv2.imshow("Window", frame)
        ...     if ord("q") == cv2.waitKey(1):
        ...         break
    """

    def __init__(self, camera_device: Optional[int] = None) -> None:
        self.media_type = MediaType.CAMERA
        self.camera_device = 0 if camera_device is None else camera_device
        self.stream = cv2.VideoCapture(self.camera_device)

    def __iter__(self) -> Iterator[np.ndarray]:
        """
        Read video and yield the frame.
        :param stream: Video stream captured via OpenCV's VideoCapture
        :return: Individual frame
        """
        while True:
            frame_available, frame = self.stream.read()
            if not frame_available:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield frame

        self.stream.release()

    def get_type(self) -> MediaType:
        return MediaType.CAMERA


class ImageStreamer(BaseStreamer):
    """
    Stream from image file.
    :param path: Path to an image.

    :example:

        >>> streamer = ImageStreamer(path="../images")
        ... for frame in streamer:
        ...     cv2.imshow("Window", frame)
        ...     cv2.waitKey(0)
    """

    def __init__(self, input_path: str, loop: bool) -> None:
        self.loop = loop
        self.media_type = MediaType.IMAGE
        if not os.path.isfile(input_path):
            raise InvalidInput(f"Can't find the image by {input_path}")
        self.image = cv2.imread(input_path, cv2.IMREAD_COLOR)
        if self.image is None:
            raise OpenError(f"Can't open the image from {input_path}")
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

    def __iter__(self) -> Iterator[np.ndarray]:
        if not self.loop:
            yield self.image
        else:
            while True:
                yield self.image

    def get_type(self) -> MediaType:
        return MediaType.IMAGE


class DirStreamer(BaseStreamer):
    """
    Stream from directory of images.
    :param path: Path to directory.

    :example:

        >>> streamer = DirStreamer(path="../images")
        ... for frame in streamer:
        ...     cv2.imshow("Window", frame)
        ...     cv2.waitKey(0)
    """

    def __init__(self, input_path: str, loop: bool) -> None:
        self.loop = loop
        self.media_type = MediaType.DIR
        self.dir = input_path
        if not os.path.isdir(self.dir):
            raise InvalidInput(f"Can't find the dir by {input_path}")
        self.names = sorted(os.listdir(self.dir))
        if not self.names:
            raise OpenError(f"The dir {input_path} is empty")
        self.file_id = 0
        for name in self.names:
            filename = os.path.join(self.dir, name)
            image = cv2.imread(str(filename), cv2.IMREAD_COLOR)
            if image is not None:
                return
        raise OpenError(f"Can't read the first image from {input_path}")

    def __iter__(self) -> Iterator[np.ndarray]:
        while self.file_id < len(self.names):
            filename = os.path.join(self.dir, self.names[self.file_id])
            image = cv2.imread(str(filename), cv2.IMREAD_COLOR)
            if self.file_id < len(self.names) - 1:
                self.file_id = self.file_id + 1
            else:
                self.file_id = self.file_id + 1 if not self.loop else 0
            if image is not None:
                yield cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def get_type(self) -> MediaType:
        return MediaType.DIR


def get_streamer(
    input_path: Union[int, str],
    loop: bool = False,
    threaded: bool = False,
) -> BaseStreamer:
    """
    Get streamer object based on the file path or camera device index provided.
    :param input: Path to file or directory or index for camera.
    :param loop: Enable reading the input in a loop.
    :param threaded: Threaded streaming option
    """
    errors: Dict = {InvalidInput: [], OpenError: []}
    streamer: BaseStreamer
    for reader in (ImageStreamer, DirStreamer, VideoStreamer):
        try:
            streamer = reader(input_path, loop)  # type: ignore
            if threaded:
                streamer = ThreadedStreamer(streamer)
            return streamer
        except (InvalidInput, OpenError) as error:
            errors[type(error)].append(error.message)
    try:
        streamer = CameraStreamer(int(input_path))
        if threaded:
            streamer = ThreadedStreamer(streamer)
        return streamer
    except (InvalidInput, OpenError) as error:
        errors[type(error)].append(error.message)

    if not errors[OpenError]:
        print(*errors[InvalidInput], file=sys.stderr, sep="\n")
    else:
        print(*errors[OpenError], file=sys.stderr, sep="\n")
    sys.exit(1)
