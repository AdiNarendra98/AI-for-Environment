# Predicting Air Pollution Levels from Satellite Images Using Deep Convolutional Neural Networks
- This study investigates the feasibility and accuracy of using a **Convolutional Neural Network upon satellite images to predict the Breezometer Air Quality Index (BAQI)**.
- Read more on [Breezometer Air Quality Index (BAQI)](https://blog.breezometer.com/breezometers-air-quality-index/)
## Propsed Methodology

![Methodology](https://github.com/arnavbansal1/SatellitePollutionCNN/blob/master/Images/Methodology.png)

## Dataset
- Data for this analysis can be obtained using open and free resources online, and the analytics can be performed on relatively inexpensive, consumer-grade hardware.  
- To perform the analysis, a set of scripts and applications were used for parallelized data collection of **10,000 satellite images at resolution 1280 x 1280 and 10,000 Breezometer air quality data records across 57 cities**.  

## Results
- A variety of models, including a six-layer convolutional network, were trained to predict the BAQI, given the satellite imagery.The number of convolutional layers, number of maxpool layers, size of convolutional layers, use of dropout, and use of data augmentation were varied, among other parameters and techniques.  
- The experiments found that one model achieved an Accuracy rate of **85.15% in binary classification** of pollution, and another model achieved an Accuracy rate of **72.70% in 10-class classification** of pollution.This study demonstrates that satellite images, which are inexpensive and ubiquitous, are accurate in predicting air pollution.

<p align="center">
<img src="https://github.com/AdiNarendra98/AI-for-Environment/blob/main/07.%20Satellite%20Data%20based%20Pollution%20Forecasting%20using%20CNNs/Images/Results.png " width="700" height="450"><br>
<b>Training vs Validation Accuracy Graphs of All Tested Models</b><br>
</p>



