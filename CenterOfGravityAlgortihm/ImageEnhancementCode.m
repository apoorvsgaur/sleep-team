I=imread('rice.png'); %this imports the image

background = imopen(I, strel('disk',15)); %will remove all objects that cannot contain the structuring element
% this makes a disk with a radius  of 15                                                     
 
I2 = I- background; %this will subtract the background 
 imshow(I2)
