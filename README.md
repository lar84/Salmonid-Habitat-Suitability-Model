# Salmonid-Habitat-Suitability-Model
A model of salmonid habitat suitability in rivers and streams that uses hydraulic models of depth and velocity as inputs, and models salmonid preference/suitability from the Washington State Dept. of Fish and Wildlife In-Stream Study Guidelines.

**How to download**

  •	Download the latest release (right side of this page) and run the application (exe file).
  
  •	You can also run in python, but make sure that the required dependencies are installed first.

**Setting up the input files:**

  •	The program requires two single-band rasters (depth/velocity) of the same extent and pixel size.
  
  •	Tested raster file types include: .tif and .img (other file types are supported, but not tested).

**Running the program:**

![image](https://user-images.githubusercontent.com/60400139/147862003-96990676-d256-42db-b8c8-c409d52838d1.png)

  •	Load the depth and velocity rasters using the ‘Open xxxxxx’ buttons.
  
  •	Select the salmonid species and life stage from the dropdown menu.
     
  •	The ‘Export As Raster’ button creates a .tif file of the habitat suitability normalized from 0 to 1.
      
**How it works:**
  1.	The input depth and velocity rasters are converted into numpy arrays.
  2.	Two linear suitability curves (for both depth and velocity) are created from the chosen species/life stage.
  3.	The numpy arrays are then normalized to the suitability curves, so that each pixels' depth/velocity values are converted into the corresponding suitability value 
  4.	The normalized depth and velocity arrays are then multiplied together to create a final suitability array.
  5.	The final numpy array is then converted back into a raster.
  
**Python libraries and dependencies used:**
  •	Numpy
  •	Tkinter
  •	Scipy
  •	GDAL
  
**References:**
Washington Department of Fish and Wildlife Instream Flow Study Guidelines:
	https://fortress.wa.gov/ecy/publications/documents/0411007.pdf

**Example:**
![image](https://user-images.githubusercontent.com/60400139/147166605-64fb6e36-b34c-43fa-84ef-ad5efeb1c689.png)

