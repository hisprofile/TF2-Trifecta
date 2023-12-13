![alt text](https://cdn.discordapp.com/attachments/590220964298752002/1033844411664171048/TF2-trifecta.png)
# TF2-Trifecta
Opening a whole new way to create TF2 art for the masses.

# What is the TF2-Trifecta?
The TF2-Trifecta is a combination of Wardrobe, Merc Deployer, and Bonemerge.

**Wardrobe** lets you index through a catalog of almost 10000 cosmetic files.

Deploy any of the nine mercs with **Merc Deployer**. You can choose to spawn from my port or Hectoris919's phoneme port.

**Bonemerge** is a Blender version of the "Easy Bonemerge Tool" for GMod.

# The Setup: TF2-V3
To start it all off, we need to install the third version of my TF2 port. This folder will contain all the mercs for Merc Deployer.

Download [TF2-V3](https://drive.google.com/file/d/1CRIgFztf5PbcXsSB8_Txe1oBnaxL6bxg/) from my google drive. Once downloaded, extract the .zip file to a directory. We are going to add this directory to Blender's asset libraries.

Open Blender, and head to the addon preferences.

<img src='https://user-images.githubusercontent.com/41131633/230690290-6b15a067-4e8b-4517-a22d-b672edaa7c78.png' width='500'>

Click on the plus to add a new asset library. Go to the TF2-V3 folder containing the 9 .blend files, and add the folder as an asset library. You should now have TF2-V3 installed for Merc Deployer.

You can add one asset and click on the magnifying glass to automatically add more in the relative path. You can click on the download button to pull existing paths from the asset library. However, on a fresh install, that should automatically happen.

Make sure you do not have a TF2-V3 folder under another TF2-V3 folder. However, it's ok if you have the last folder added as an asset library. For organization's sake, it's better to have the path set up like this:

`DRIVE:\path_to_folder\TF2-V3\.blend files`

instead of:

`DRIVE:\path_to_folder\TF2-V3\TF2-V3\.blend files`

# The Setup: The TF2 Collection
What is arguably the longest part of the setup process will be the most important. The TF2 Collection is a massive collection of every TF2 cosmetic, weapon, and prop.

Download [The TF2 Collection](https://drive.google.com/drive/folders/1W0aNvtbGdBOdObtBBh7nsz9w661E6P_j) from my google drive.

<img src="https://user-images.githubusercontent.com/41131633/204808615-cd24abf9-6cfd-4c73-8de6-f12d2990161b.png">

You are not required to download `props_` or `weapons`.

I recommend that you download and unzip each folder individually. Alternatively, you can download the whole thing at once, but that is something I recommend against as it will split the folder into multiple .zip files.

When you have The TF2 Collection downloaded and with Blender's preferences still open, add each individual folder as an asset library.

If all has gone correctly, the preferences should look like this:

<img src="https://user-images.githubusercontent.com/41131633/204809838-a48fed5f-10a1-44c8-a402-061c903c3c33.png" width="400">

At which point, we head to the final step:

# The Setup: TF2-Trifecta

Download the lastest release of the [TF2-Trifecta](https://github.com/hisprofile/TF2-Trifecta/releases). Don't unzip the folder this time.

Head back to the preferences and click on the `Add-ons` tab. Click `Install...`

<img src='https://user-images.githubusercontent.com/41131633/204811420-1d1fa1f3-8f72-4924-8cee-450bea6b99c9.png' width='400'>

Find `TF2-Trifecta.zip` and install the `.zip` file.

With everything hopefully gone well, we now conclude `The Setup` and head onto the guides for each addon.

# Location
You can find each tool in the side panel of the viewport.

<img src='https://user-images.githubusercontent.com/41131633/204814256-d1a474a8-a7ed-42b3-999e-1c7cf980fe80.png'>

# Wardrobe
Wardrobe is like the world's largest closet known for how easy it is to search through it. To search for something, enter something into the search bar and click `Search for cosmetics`.

<img src='https://user-images.githubusercontent.com/41131633/204816043-725cb0b3-966f-4cc3-b41c-ff606e17da1b.png' width='400'>

Click on a cosmetic button to spawn one in. Having a class selected while spawning a cosmetic will automatically bind the cosmetic to said class.

<img src='https://user-images.githubusercontent.com/41131633/204816652-953bf916-f488-4e8e-9fbf-cfc10f113790.png' height='400'>

To match the colors of a class, click `Use Lightwarps (TF2 Style)`. However, if you plan to use cycles for a render, do not click anything.

<img src='https://user-images.githubusercontent.com/41131633/204817163-86c2edf2-23ac-4496-9d10-b788708396fe.png' width='400'><img src='https://user-images.githubusercontent.com/41131633/204817257-3cd14e83-bb35-4766-b373-fa78b6ecc243.png' width='400'>

To closely match the TF2 look, use the Standard color transform instead of the Filmic color transform.

<img src='https://user-images.githubusercontent.com/41131633/204817569-82245061-f2e4-407e-8ff9-c723033ae5fe.png' width='400'>

If paintable regions of a cosmetic appear solid black, go to `Material Fixer/Selector` and attempt to fix the material that is causing issues.

<img src='https://user-images.githubusercontent.com/41131633/204818271-076f283e-e6b9-4431-83fe-d7a99bc11f5f.png' width='400'><img src='https://user-images.githubusercontent.com/41131633/204818721-20eaf373-da46-46d4-8384-fbaf63565281.png' width='400'>

You can paint the active material using the `Paints` window.

<img src='https://user-images.githubusercontent.com/41131633/204819046-2816e9b4-755a-4a2a-8479-35c94c5dee33.png' width='400'>

Not all cosmetics are named correctly yet! Please report a cosmetic you wish to be renamed.

# Merc Deployer

Deploy any of the nine mercs into your scene. You can choose between an IK rig or a taunt compatible (FK) rig. You can read on how to import animations onto a rig in the [Source2Blender](https://source2blender.readthedocs.io/en/latest/TF2Vanilla/Animations.html) docs.

<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/661c0183-3c60-40c0-a73f-10959cc14361' width='400'>

# Bonemerge
Attach cosmetics to a class by choosing a target armature and and selecting the cosmetics to attach.

<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/a0c09a69-b839-462c-ab70-c8370f8fa28b' width='400'>

# Face Poser
(Only supported for my rigs!)
The Face Poser tool is designed to control faces using my HWM scheme. the control layout is inspired by SFM, and functions similarly as well.

## Face Poser
<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/89f10e43-0ad0-4751-af06-9c5414aecccc'>

The tool supports both stereo and mono flexing, and uses a weight slider for stereo flexes. Stereo flexes use one slider who's value will always remain at 0. Any value given to the slider will be taken as additive and applied to the flex controllers they control.

The circular button is a shortcut for the auto-keyframing option. The diamond creates a keyframe on all sliders on the current frame. `Upper`, `Mid` and `Lower` can be used to filter out sliders. Switching to `Shapekeys` view will show all undriven shapekeys. Using `Optimize Merc` will remove all drivers on the shape keys, giving a small boost in performance until you wish to restore facial movements. At which point you will press `Restore Merc`

## Pose Library
<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/221e3b9b-3aa9-4960-ad40-d944091e4303' height=200> <img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/7c2ef386-c2f5-4181-8cd0-ed33c4a96fd3' height=200>
The Pose Library allows users to save and apply face pose combinations. This is very useful for fast lipsyncing or emotions. Upon applying a saved face pose, you can choose to keyframe the change. Enabling `Reset All` will reset the face before applying the pose. Enabling `Keyframe Unchanged` will keyframe the entire face, despite some areas not having been moved.

## Face Randomizer & Lock List
<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/0f11f9c9-d397-4909-aca8-8ec76da9bd60' width=300>

The `Face Randomizer` does what the name says. However, the `Lock List` will prevent locked sliders from getting randomized. Find the slider you want to lock and press the lock icon,

# Rigs
There are three official rigs that can be used with Merc Deployer: Mine, Eccentric's and ThatLazyArtist's. All of them are the same except for how they control the face. And their core, they are all a Rigify rig.

My set of rigs is meant to be controlled just like how you would control faces in SFM. Therefore, I say that my rigs are recommended for users with experience in SFM.

Eccentric's rigs use a face panel with control points over the face, making it closer to the industrial standard for animating faces.

ThatLazyArtist's use a face panel with sliders and switches off to the side. Although each slider may be vague in what part of the face controls, you can see the name of the slider in the top right corner.

# Updating Files
You can easily update The TF2 Collection and TF2-V3 by going to `Scene Properties > TF2 Trifecta Updater`

<img src='https://user-images.githubusercontent.com/41131633/204821666-a253a78d-1491-430a-a31d-501942c49b44.png' width='400'>

The files will be downloaded off of Gitlab and will automatically delete and replace the old files. Open the console to view progress.

# End

Thank you Unhelpful Git for coining the name "TF2 Trifecta"

Using library "dload" to download file from tf2 collection repository.



https://github.com/x011/dload
