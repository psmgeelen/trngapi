# TRNG
What is random and why does it matter? Well, randomness presents 
opportunity. Firstly for encryption, safety is assured based on randomness. 
If the randomness is not truly random, but biased, then the assumed 
complexity of the randomness is less, reducing safety. Furthermore, 
randomness is can be a feature for Artificial Intelligence and Machine 
Learning. Algorithms often are build around the idea of features and 
weights, in which the latter are randomly attributed and tuned to improve 
predictions. If these weights are not random, there is a chance that the 
model that is being trained, is already biased. This can harm the speed of 
convergence as well as the overall performance of the model.

This repo is focussed around building a free service that everybody can use 
to use for encryption and AI/ML purposes. The True Random Number Generator 
that we use is the `Infinite Noise TRNG`, that can be purchased [here](https://leetronics.de/de/shop/infinite-noise-trng/)

The core-concept of the device is around an overloaded amplifier that 
craetes noise. This noise is not random yet though, so it will be convered 
with an ASIC SHA3 chip to make it truely random.
![Infinite Noise TRNG](https://13-37.org/wp-content/uploads/2018/04/trng-data-flow.png)

The API wraps the `Infinite Noise TRNG` SDK that can be found [here]
(https://github.com/waywardgeek/infnoise) in a FastAPI and deploys this in 
a docker container. The installation process is as follows:

* Install Drivers for machine
* Run/Deploy Docker container
* Consumes API service

With this project I am to create awareness around the topic of Randomness 
and the importance of doing randomness 'well'.