# OpenVINO™ Training Extensions
[![python](https://img.shields.io/badge/python-3.8%2B-green)]()
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)]()
[![mypy](https://img.shields.io/badge/%20type_checker-mypy-%231674b1?style=flat)]()
[![openvino](https://img.shields.io/badge/openvino-2021.4-purple)]()

OpenVINO™ Training Extensions provide a convenient environment to train
Deep Learning models and convert them using the [OpenVINO™
toolkit](https://software.intel.com/en-us/openvino-toolkit) for optimized
inference.

## Detailed Workflow
![](training_extensions_framework.png)

1. To start working with OTE, prepare and annotate your dataset. For example, on CVAT.

2. OTE train the model, using training interface, and evaluate the model quality on your dataset, using evaluation and inference interfaces.

Note: prepare a separate dataset or split the dataset you have for more accurate quality evaluation.

3. Having successful evaluation results received, you have an opportunity to deploy your model or continue optimizing it, using NNCF and POT. For more information about these frameworks, go to [Optimization Guide](https://docs.openvino.ai/nightly/openvino_docs_model_optimization_guide.html).

If the results are unsatisfactory, add datasets and perform the same steps, starting with dataset annotation.

## Prerequisites
* Ubuntu 18.04 / 20.04
* Python 3.8+
* [CUDA Toolkit 11.1](https://developer.nvidia.com/cuda-11.1.1-download-archive) - for training on GPU

## Repository components
* [OTE SDK](ote_sdk)
* [OTE CLI](ote_cli)
* [OTE Algorithms](external)

## Quick start guide
In order to get started with OpenVINO™ Training Extensions click [here](QUICK_START_GUIDE.md).

## License
Deep Learning Deployment Toolkit is licensed under [Apache License Version 2.0](LICENSE).
By contributing to the project, you agree to the license and copyright terms therein
and release your contribution under these terms.

## Tutorials
[Object Detection](https://github.com/openvinotoolkit/training_extensions/blob/master/ote_cli/notebooks/train.ipynb)

## Misc

Models that were previously developed can be found on the [misc](https://github.com/openvinotoolkit/training_extensions/tree/misc) branch.

## Contributing

If you want to contribute, refer to [Contributing guide](https://github.com/openvinotoolkit/training_extensions/blob/master/CONTRIBUTING.md) before starting work on a pull request.

Deep Learning Deployment Toolkit is licensed under [Apache License Version 2.0](https://github.com/openvinotoolkit/training_extensions/blob/master/LICENSE).
By contributing to the project, you agree to the license and copyright terms therein
and release your contribution under these terms.

## Known limitations

Currently, training, exporting, evaluation scripts for TensorFlow\*-based models and the most of PyTorch\*-based models from the [misc](#misc) branch are exploratory and are not validated.

---
\* Other names and brands may be claimed as the property of others.
