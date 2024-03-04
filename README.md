![alt text](https://cdn.discordapp.com/attachments/590220964298752002/1033844411664171048/TF2-trifecta.png)
# TF2-Trifecta
Opening a whole new way to create TF2 art for the masses.

# What is the TF2-Trifecta?
The TF2-Trifecta is a multi-purpose tool to masterfully manipulate Team Fortress 2 assets.

**Wardrobe** lets you index through a catalog of almost 10000 cosmetic files.

Deploy any of the nine mercs with **Merc Deployer**. You can choose to spawn from my port or Hectoris919's phoneme port.

**Bonemerge** is a Blender version of the "Easy Bonemerge Tool" for GMod.

# The Setup
Installing the TF2-Trifecta and its prerequesites is as easy as pressing one button, followed by a few minutes of waiting.

Download the lastest release of the [TF2-Trifecta](https://github.com/hisprofile/TF2-Trifecta/releases) and install the addon as a .zip file. Head to the preferences and click on the `Add-ons` tab. Click `Install...`

<img src='https://user-images.githubusercontent.com/41131633/204811420-1d1fa1f3-8f72-4924-8cee-450bea6b99c9.png' width='400'>

Find `TF2-Trifecta.zip` and install the `.zip` file.

Once installed, go to the <img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/68579230-c715-48fb-b158-446323efbf61' width=30> Scene Properties and locate the `TF2-Trifecta` tab and expand the panel. At the bottom, you'll find a box where you can install the `TF2 Collection`. <img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/cdb9f995-190d-477e-837f-441bce7b2e54' width=350>

After setting the path to an empty folder, you should be able to install the `TF2 Collection` just by pressing the install button. Enable `Include Rigs` if you wish. Wait a few minutes for everything to install and you should be good to go!

# Location
You can find each tool in the side panel of the viewport.

<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/3cd4f866-561e-47ee-baf5-5614715d94bc'>

# Wardrobe
Wardrobe is like the world's largest closet known for how easy it is to search through it. To search for something, enter something into the search bar and click `Search for cosmetics`.

<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/c06851c9-ae59-4914-b7a1-5efd6fc602ef' width='200'>

Click on a cosmetic button to spawn one in. Having a class selected while spawning a cosmetic will automatically bind the cosmetic to said class.

<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/cc3ec1dc-0f4c-4c26-bfb4-f5d2813831db' height='400'>

To match the colors of a class, click `Use Lightwarps (TF2 Style)` in the `Material Settings`. However, if you plan to use cycles for a render, do not click anything.

<img src='https://user-images.githubusercontent.com/41131633/204817163-86c2edf2-23ac-4496-9d10-b788708396fe.png' width='400'><img src='https://user-images.githubusercontent.com/41131633/204817257-3cd14e83-bb35-4766-b373-fa78b6ecc243.png' width='400'>

To closely match the TF2 look, use the Standard color transform instead of the Filmic color transform.

<img src='https://user-images.githubusercontent.com/41131633/204817569-82245061-f2e4-407e-8ff9-c723033ae5fe.png' width='400'>

If paintable regions of a cosmetic appear solid black, go to `Material Fixer/Selector` and attempt to fix the material that is causing issues.

<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/9f847e65-cb0d-41d9-a1b5-d801b234833a' width='400'><img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/5daf1dfd-4770-47cb-aecd-0aeb41ecdf19' width='400'>

You can paint the active material using the `Paints` window.

<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/26d909bc-e4e2-43dc-bbfa-2240cf6f340c' width='400'>

Not all cosmetics are named correctly yet! Please report a cosmetic you wish to be renamed.

# Merc Deployer

Deploy any of the nine mercs into your scene. You can choose between an advanced rigify (New) rig or a taunt compatible (Legacy) rig. You can read on how to import animations onto a rig in the [Source2Blender](https://source2blender.readthedocs.io/en/latest/TF2Vanilla/Animations.html) docs.

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
You can easily update The TF2 Collection and rigs by going to `Scene Properties > TF2 Trifecta Updater`

<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/c6f18f9d-bf78-4c5e-8b69-3089c6603dd7' height=500>

# End

Thank you Unhelpful Git for coining the name "TF2 Trifecta"
