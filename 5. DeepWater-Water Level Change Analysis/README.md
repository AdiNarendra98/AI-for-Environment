# Deep Water

This repo is the reimplementation of the [Deep-Water Repo by Maximiliano Beber](https://github.com/maxbeber/deep-water) a project aims to track changes in water level using satellite imagery and deep learning.

## Introduction

The motivation for this project is the article [Some of the World's Biggest Lakes Are Drying Up](https://www.nationalgeographic.com/magazine/2018/03/drying-lakes-climate-change-global-warming-drought/) found in the March 2018 edition of the [National Geographic](https://www.nationalgeographic.com/) magazine.

> Freshwater is the most important resource for mankind, cross-cutting all social, economic and environmental activities. It is a condition for all life on our planet, an enabling limiting factor for any social and technological development, a possible source of welfare or misery, cooperation or conflict. ([UNESCO](https://en.unesco.org/))

The exponenetial growth of satellite-based information over the past four decades has provided unprecedented opportunities to improve water resource manegement.

## Datasets
1. [**NWPU-Resic-45**](https://www.tensorflow.org/datasets/catalog/resisc45):
 - Benchmark for Remote Sensing Image Scene Classification (RESIC), 
 - Created by [Nortwestern Polytechnical University](https://en.nwpu.edu.cn/) (NWPU). 
 - This dataset contains **31,500 images, covering 45 scene classes (including water classes) with 700 images in each class**.

2. **Time-series of cloudless Sentinel-2 imagery including 17 criticaly endangered lakes** as following:

- [Lake Poopo](https://en.wikipedia.org/wiki/Lake_Poop%C3%B3), Bolivia;
- [Lake Urmia](https://en.wikipedia.org/wiki/Lake_Urmia), Iran;
- [Lake Mojave](https://en.wikipedia.org/wiki/Lake_Mohave), USA;
- [Aral sea](https://en.wikipedia.org/wiki/Aral_Sea), Kazahkstan;
- [Lake Copais](https://en.wikipedia.org/wiki/Lake_Copais), Greece;
- [Lake Ramganga](https://en.wikipedia.org/wiki/Ramganga_Dam), India;
- [Qinghai Lake](https://en.wikipedia.org/wiki/Qinghai_Lake), China;
- [Salton Sea](https://en.wikipedia.org/wiki/Salton_Sea), USA;
- [Lake Faguibine](https://earthobservatory.nasa.gov/images/8991/drying-of-lake-faguibine-mali), Mali;
- [Mono Lake](https://en.wikipedia.org/wiki/Mono_Lake), USA;
- [Walker Lake](https://en.wikipedia.org/wiki/Walker_Lake_(Nevada)), USA;
- [Lake Balaton](https://en.wikipedia.org/wiki/Lake_Balaton), Hungary;
- [Lake Koroneia](https://en.wikipedia.org/wiki/Lake_Koroneia), Greece;
- [Lake Salda](https://en.wikipedia.org/wiki/Lake_Salda), Turkey;
- [Lake Burdur](https://en.wikipedia.org/wiki/Lake_Burdur), Turkey;
- [Lake Mendocino](https://en.wikipedia.org/wiki/Lake_Mendocino), USA;
- [Elephant Butte Reservoir](https://en.wikipedia.org/wiki/Elephant_Butte_Reservoir), USA.

## Labeling

The [**MakeSense**](https://www.makesense.ai/) online tool has been used for labeling both datasets images. It only requires a web browser and you are ready to go. It's an excellent choice for small computer vision deep learning projects, making the process of preparing the dataset easier and faster.

## Data Augmentation

The following techniques have been applied during training:

- **Height shift up to 30%**
- **Horizontal flip**
- **Rotation up to 45 degrees**
- **No shea**
- **Vertical Flip**
- **Width shift up to 30%**
- **Zoom between 75% and 125%**

## Metrics

The following metrics have been used to evaluate the Semantic Segmenation model:

- **Jaccard Index**
- **Dice Coefficient**

More information about both of these metrics can be found [here](https://towardsdatascience.com/metrics-to-evaluate-your-semantic-segmentation-model-6bcb99639aa2).

## Baseline

The baseline consists of a simple U-Net model architecture. This strategy allow us to modify the model for our own purposes and fine-tunning it as necessary for our development purposes. By using this network architecture, we could spend more time understanding the optimization strategies.

### Without Data Augmentation

Train/Validation/Test splits based on Resic-45 dataset only:
- Training set: 489 images
- Validation set: 140 images
- Test set: 71 images

### <ins>Model performance</ins>:

![Baseline results without Image Augmentation](https://github.com/maxbeber/deep-water/blob/develop/assets/documentation/baseline-no-augmentation.png)

### With Data Augmentation

Train/Validation/Test splits based on Resic-45 dataset only:
- **Training Set**: 979 images;
- **Validation Set**: 280 images;
- **Test Set**: 122 images.

### <ins>Model performance</ins>:

![Baseline results using image augmentation](https://github.com/maxbeber/deep-water/blob/develop/assets/documentation/baseline-with-augmentation.png)

It can be seen clearly that the baseline model overfits using image augmentation.

## Model Optimization

The following strategies have been explored:

1. Using Early Stopping and adaptive learning rates;
2. Using a bigger model (and dropout);
3. Using regularization (Batch Normalization);
4. Using residual connections;
4. Dealing with class imbalance using dice loss;
6. Refining label images using CRFs;
7. Ensemble predictions.

Train/Validation/Test splits:
- Training set: 489 images from Resic-45 dataset randomly transformed at each epoch using one of the techniques described in the fourth section _Data Augmentation_;
- Validation set: 211 images from Resic-45 dataset;
- Test set: 359 images from Sentinel-2 dataset.

### <ins>Model performance using "Binary Cross Entropy" as the loss function</ins>:

![Model optimization using binary cross entropy](https://github.com/maxbeber/deep-water/blob/develop/assets/documentation/model-optimization-binary-cross-entropy.png)

### <ins>Model performance using "Dice Loss" as the loss function</ins>:

![Model optimization using dice loss](https://github.com/maxbeber/deep-water/blob/develop/assets/documentation/model-optimization-dice-loss.png)

## Model Results

The test set to measure the results presented below is based on 182 images from Sentinel-2 dataset.

### <ins>Model 1: U-Net residual model trained "without Label Correction"</ins>:

![Model results: unet residual large dice](https://github.com/maxbeber/deep-water/blob/develop/assets/documentation/model-results-unet-residual-large-dice.png)

### <ins>Model 2: U-Net residual model trained "with Label Correction using Conditional Random Fields"</ins>:

![Model results: unet residual large dice](https://github.com/maxbeber/deep-water/blob/develop/assets/documentation/model-results-unet-residual-large-dice-with-crf.png)

### <ins>Model 3: Ensemble model based on the Two Previous Models</ins>:

![Model results: unet residual large dice](https://github.com/maxbeber/deep-water/blob/develop/assets/documentation/model-results-combined-model.png)

- The ensemble model is the one with highest accuracy (**97.15%**) and is the one used in the Dashboard application that will be covered in the next section.

## Dashboard

The dashboard can be executed with the following command:

```python app.py```

A Demo is available [here](https://drive.google.com/file/d/1iATFNuEvBrYWUtnZvZTDVe_R_z8LpgAA/view?usp=sharing).

**Use Case 1: Lake Copais, Greece (2019)**

![Use Case 1: Lake Copais](https://github.com/maxbeber/deep-water/blob/develop/assets/documentation/use-case-lake-copais.png)

**Use Case 2: Lake Di Cancano, Italy (2019)**

![Use Case 2: Lake Di Cancano](https://github.com/maxbeber/deep-water/blob/develop/assets/documentation/use-case-lake-di-cancano.png)

**Use Case 3: Lake Salda, Turkey (2016)**

![Use Case 3: Lake Salda](https://github.com/maxbeber/deep-water/blob/develop/assets/documentation/use-case-lake-salda.png)

## Requirements

The following libraries are required to create the virtual environment. The creation of the virtual environment is detailed in the next section.

- Cython
- Dash
- Matplotlib
- NumPy
- Pillow
- Plotly
- [Pydensecrf](https://github.com/lucasb-eyer/pydensecrf)
- Rasterio
- Requests
- Tensorflow 2.4

## Virtual Environement

To setup your local environemnt it is recommended to create a virtual environment using condas. Make sure you have it installed on your computer and then execute the command below:

```conda env create -f environment.yml```

The `environment.yml` file ensures that all dependiences will be downloaded.

After the enviroment is created, it is necessary to activate the virtual environemnt as follows:

```conda activate deep-water```

The virtual environment can be deactivate in a single line of code.

```conda deactivate```


