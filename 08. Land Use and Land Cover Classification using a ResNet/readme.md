# Land Use and Land Cover Classification using a ResNet and fastai
- The aim of the study is to **test the accuracy of Convolutional Neural Networks to learn the spatial and spectral characteristics of image patches of the Earth surface extracted from satellite images for Land Use and Land Cover (LULC) classification tasks**. 

## Dataset Used

- **EuroSAT dataset** created at the **Deutsches Forschungszentrum für Künstliche Intelligenz (DKFI)** was used for this study.
- The images were **extracted from the Sentinel-2A L1C** products covering cities in **34 European countries** all over a year. 
- The dataset consists of two subsets: RGB and multispectral. Each dataset contains **27000 images divided in 10 classes with 2000 to 3000 images per class.** 
- The classes defined to label the images are a subset of those defined in **CORINE: Pasture, HerbaceousVegetation, Industrial, AnnualCrop, Residential, PermanentCrop, Highway, SeaLake, Forest, River**.
- For this study we used the RGB Dataset. The RGB dataset contains images covering the three bands in the visible region of the spectrum (RGB colors)
- EuroSAT RGB Dataset Download Link:[**DFKI Website**](https://madm.dfki.de/downloads)
- The images are compressed in a zip file and divided in 10 folders named after the classes defined for the classification task.
- Apart from that additional images have been already created in the previous step from the original ones by using the **Data Augmentation techniques** implemented by the [fastai's](https://docs.fast.ai/vision.augment.html) ``aug_transforms()``function.

<p align="center">
<img src="https://github.com/AdiNarendra98/AI-for-Environment/blob/main/08.%20Land%20Use%20and%20Land%20Cover%20Classification%20using%20a%20ResNet/Images/data_augmentation.png " width="600" height="550"><br>
<b>Sample of Images formed by Data Augumentation</b><br>
</p>

## Model Used

- Used [**ResNet50**](https://arxiv.org/abs/1512.03385) for this study.
<p align="center">
<img src="https://github.com/AdiNarendra98/AI-for-Environment/blob/main/08.%20Land%20Use%20and%20Land%20Cover%20Classification%20using%20a%20ResNet/Images/Resnet%2050%20archi.png " width="700" height="400"><br>
<b>ResNet50 Architecture </b><br>
</p>

## Results
- **Accuracy = ~98%**
<p align="center">
<img src="https://github.com/AdiNarendra98/AI-for-Environment/blob/main/08.%20Land%20Use%20and%20Land%20Cover%20Classification%20using%20a%20ResNet/Images/Training%20vs%20Epochs%20Graph.png " width="650" height="400"><br>
<b>Accuracy vs Epochs Graph</b><br>
</p>

<p align="center">
<img src="https://github.com/AdiNarendra98/AI-for-Environment/blob/main/08.%20Land%20Use%20and%20Land%20Cover%20Classification%20using%20a%20ResNet/Images/confusion_matrix.png " width="600" height="600"><br>
<b>Confusion Matrix of the Model</b><br>
</p>

### Predictions

| **Original Ground Truth Image** | **Generated Mask Image** |
| ------------- | ------------- |
| <p align="center"><img src="https://github.com/AdiNarendra98/AI-for-Environment/blob/main/08.%20Land%20Use%20and%20Land%20Cover%20Classification%20using%20a%20ResNet/Images/Input%201.jpg "><br><b>Land with Highway </b><br> | ![real1](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/08.%20Land%20Use%20and%20Land%20Cover%20Classification%20using%20a%20ResNet/Images/Output1.png)  |
| <p align="center"><img src="https://github.com/AdiNarendra98/AI-for-Environment/blob/main/08.%20Land%20Use%20and%20Land%20Cover%20Classification%20using%20a%20ResNet/Images/Input%202.jpg "><br><b>Same Land with Factory(After 2 years) </b><br> | ![real1](https://github.com/AdiNarendra98/AI-for-Environment/blob/main/08.%20Land%20Use%20and%20Land%20Cover%20Classification%20using%20a%20ResNet/Images/op2.png)  |

## Inspiration

- This work is reimplemented and inspired from the work done by [**Luigi Selmi**](https://github.com/luigiselmi).


