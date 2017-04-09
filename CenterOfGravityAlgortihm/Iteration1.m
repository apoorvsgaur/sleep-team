%Step 1
image=imread('PictureOfBaby.png'); %imports the imagec
%Step 2
greyImage= rgb2gray(image); %converts image from RGB to greyscale
imshow(greyImage)
%Step 3
[row,column]=size(greyImage); %gives us the total amount of rows and columns of the image matrix
frequency = zeros(1,255); %intializes the array for the greyscale values of 0 (white) and 255 black
i=1; %intializing the variables for the row counter
n=1; %intializing the variables for the column counter
sum = 0;
while i <= row 
   while n<=column
        value=greyImage(i,n);
        frequency(value) = frequency(value) +1;
        n = n+1;
        sum = sum + 1;
   end
   n = 1;
   i = i+1;    
end
greyScaleValues=transpose(frequency); 
%the above code uses while loops to go through each row and then resets 

