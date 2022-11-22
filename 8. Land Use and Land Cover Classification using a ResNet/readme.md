# Land Use and Land Cover Classification using a ResNet and FastAi
- The aim of the study is to **test the accuracy of Convolutional Neural Networks to learn the spatial and spectral characteristics of image patches of the Earth surface extracted from satellite images for Land Use and Land Cover (LULC) classification tasks**. 

## Dataset Used

- EuroSAT dataset created at the **Deutsches Forschungszentrum für Künstliche Intelligenz (DKFI)** was used for this study.
- The images were **extracted from the Sentinel-2A L1C** products covering cities in **34 European countries** all over a year. 
- The dataset consists of two subsets: RGB and multispectral. Each dataset contains **27000 images divided in 10 classes with 2000 to 3000 images per class.** 
- The classes defined to label the images are a subset of those defined in **CORINE: Pasture, HerbaceousVegetation, Industrial, AnnualCrop, Residential, PermanentCrop, Highway, SeaLake, Forest, River**.
- For this study we used the RGB Dataset. The RGB dataset contains images covering the three bands in the visible region of the spectrum (RGB colors)
- EuroSAT RGB Dataset Download Link:[**DFKI Website**](https://madm.dfki.de/downloads)
- The images are compressed in a zip file and divided in 10 folders named after the classes defined for the classification task.
