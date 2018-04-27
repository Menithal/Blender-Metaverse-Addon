## MMD to High Fidelity Guide


## Requirements

To import MMD models as avatars need a couple of tools: 

- You need bandizip to unpack file names with Japanese utf-8 characters.  https://www.bandisoft.com/bandizip/ This is done because [Windows Zip & others using the same compression methodology do not like non-latin characters.](https://support.microsoft.com/en-us/help/2704299/japanese-characters-in-file-names-are-displayed-as-garbled-text-after) and Applocale not available in Windows 10 anylonger! 
- You need to install the latest mmd_tool to import the .pmd file types to Blender
https://github.com/powroupi/blender_mmd_tools . Follow their readme to install it.


#### Opening the Zip file 

Open up bandizip, press Open Archive and open the mmd model zip file you want to extract

Before pressing Extract, make sure your "Code Page" is set to Japanese

---

#### Make sure to read the MMD Model's Readme: 
**Some artists explicitly state they do not want redistribution, nor modification, nor do they want to be put into another game other than MMD, or put into Adult situations.** Sure it is the internet, but  respect should be given to these creators. 

The Readmes usually have an English translation below the japanese one if not, more of it will be visible in the read me after import to blender.

---

#### Importing to Blender

After Extracting the zip file and reading the read me, open up a new scene in Blender

1. Clean the scene, you can press A, then X, then left mouse button 
2. Goto File > import .pmd and navigate to the directory
3. Before Importing Make sure the import settings are as follows:
> 
> Scale: 0.1 (Very, important)
> Clean Model
> Remove Doubles
> 
> Fix IK Links, Rename Bones / Translate bones should all be disabled.
> 
> MIP maps is voluntary.

You can then save these settings by pressing the plus sign above morphs and assigning it a name. It will then be available from the dropdown

4. After importing to scene, in the 3D View, navigate to the `High Fidelity` Tab.
5. Save Blend file to a directory you want to use for your avatar
6. Press `Convert MMD Avatar`. 
7. After pressing the button, Blender will start doing stuff in the foreground. Wait until the console window has dissapeared. **It will do alot of work.**

The following things will happen:
- The bones will correct them selves and materials will combine them selves as much as possible. 
- TGA textures will be converted to png automatically,
- and all textures used will be moved to textures folder relative to the model.

After it is done, play around with the bones in pose mode to see if everything binded correctly. Once you are happy with the result

1. Select the armature
2. Goto Edit mode
3. Select bones you want to make physical (hair, tails, clothing, etc)
4. In the Left hand panel, All the other options under `High Fidelity` will be hidden, except a few buttons
5. Press `Set Bone Physical`
6. Now you are ready to export: Goto `File > Export > Hifi Avatar FST`, Set `Embed` to True. Export to Folder

Once this is done, upload both the `fst file` and the `fbx` either to the marketplace, or to a http directory.



