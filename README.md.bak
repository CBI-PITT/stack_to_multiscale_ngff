# tiff_utils

## This class is a simple way of working with tiff files



```python
## Import
from`tiff_utils import tiff
```

##### -During reads, all tags are collected and resolution is extracted in microns

1. by default, specifying a file name loads the image, tags and resolution information.

   ```python
   myImage =`tiff(fileName.tif) 
   print(myImage.shape)
   print(myImage.image.dtype)
   print(myImage.y_resolution, myImage.x_resolution)
   print(myImage.tags)
   ```

2. loadImage=False can be specified when instantiating the class to load only tags and resolution information.

   ```python
   myImage = tiff(fileName.tiff, loadImage = False)
   ```

3. An image can be loaded manually by calling class method: .loadImage()

   ```python
   myImage.loadImage()
   ```

   

##### -During writes, the class.write() method will automatically:

1. Determine if BigTiff is required (currently files >= 2GB)

   ```
   myImage.write() # Automatically determines whether BigTiff is required
   myImage.write(bigTiff=True) # Force the writer to use BigTiff
   ```

2. Manage compression (currently defaults to 'zlib')

   ```
   myImage.write() # Defaults to zlib compression
   myImage.write(compression=0) # No compression
   ```

3. Manage tiled-tiff writes (currently defaults to (512,512))

   ```python
   myImage.write()
   myImage.write(tile=None)
   myImage.write(tile=(1024,1024))
   ```

​    CAUTION: be careful when calling .write() because it will overwrite the original image
​        if the file name was not changed.



##### -Class methods enable easy:

1. Replacement of image with a different np.array: .newImage(array)

   ```python
   myImage =`tiff(fileName.tif)
   myImage.newImage(array = np.random.random((10,1024,1024),dtype=np.uint16))
   ```

2. Assign a new file name: .newFileName(fileNameString)

   ```python
   myImage.newFileName('/a/new/place/to/store/my/file.tif')
   ```

3. Conversion of dtype:

   ```python
   myImage.to8bit()
   myImage.to16bit()
   myImage.toFloat()
   myImage.toFloat32()
   myImage.toFloat64()
   myImage.toDtype(np.uint16)
   myImage.toDtype(np.uint8)
   myImage.toDtype(np.float)
   ```

4. Assigning of new resolution in microns: .newResolution((yres,xres))

   ```python
   myImage.newResolution((0.5,0.5))
   ```

5. Resizing of image to a specified resolution in microns: .resizeImage((x_res,y_res)) or .resizeImage(int)

   ```python
   myImage.resizeImage((25,25)) #Resize to 25 microns y,x
   ```

6. Clone an image class: newClass = currentClass.clone(newFilePath=None, array=None, newResolutionMicrons=None)

   ```
   newImageClass = myImage.clone()
   ```

   