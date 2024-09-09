![alt text](https://github.com/user-attachments/assets/2d1ef0c8-e347-43e9-b9d8-de74fda846b5)
# What is the TF2-Trifecta?
The TF2-Trifecta is a Blender addon to spawn and manipulate my mercenaries, cosmetics, and weapons ports. It has four tools:
## Wardrobe
- Spawn cosmetics & weapons, both RED & BLU versions
- Paint cosmetics
## Merc Deployer
- Allows you to spawn two types of pre-prepared rigs, Rigify rigs and in-game rigs (taunt compatible). They are aptly named `New` and `Legacy`
- Can choose between sets of rigs (At this moment, only three exist. Mine, Eccentric's and ThatLazyArtist's.)
## Bonemerge
- Allows you to attach cosmetics and weapons to a mercenary with ease
- Allows you to attach facial cosmetics to rigs that support it
- Has a multi-layered attachment system
## Face Poser
- Allows you to pose the face on my rigs as you would in SFM and Garry's Mod
- Allows you to apply preset faces for quick emotions/visemes
- Has a face randomizer for funny faces

# The Setup
Installing the TF2-Trifecta and its prerequesites is as easy as pressing one button, followed by a few minutes of waiting.

Download the lastest release of the [TF2-Trifecta](https://github.com/hisprofile/TF2-Trifecta/releases) and install the addon as a .zip file. Head to the preferences and click on the `Add-ons` tab. Click `Install...`

<img src='https://user-images.githubusercontent.com/41131633/204811420-1d1fa1f3-8f72-4924-8cee-450bea6b99c9.png' width='400'>

Find `TF2-Trifecta.zip` and install the `.zip` file.

Once installed, go to the <img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/68579230-c715-48fb-b158-446323efbf61' width=30> Scene Properties and locate the `TF2-Trifecta` tab and expand the panel. At the bottom, you'll find a box where you can install the `TF2 Collection`. <img src='https://github.com/user-attachments/assets/35471e44-6eb8-4183-9c2f-adbdacbc6b87' width=375>

After setting the path to an empty folder, you should be able to install the `TF2 Collection` just by pressing the install button. Enable `Include Rigs` if you wish. Wait a few minutes for everything to install and you should be good to go!

# Location
You can find each tool in the side panel of the viewport.

<img src='https://github.com/user-attachments/assets/1ad007b1-6066-4466-bf19-ffe45606731a' width=300>

# Wardrobe
Wardrobe is an expansive tool used for searching for TF2 Items in the downloaded ports. To search for something, enter something into the search bar and click `Search for cosmetics`.

<img src='https://github.com/user-attachments/assets/84522845-a705-4abe-afcb-2b0e6c0118da' width='235'>

Click on a cosmetic button to spawn one in. Having a class selected while spawning a cosmetic will automatically bind the cosmetic to said class.

You can disable this "Auto-bind" function by holding `SHIFT` while spawning the cosmetic.

<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/cc3ec1dc-0f4c-4c26-bfb4-f5d2813831db' height='400'>


You can paint the active material using the `Paints` window.

<img src='https://github.com/user-attachments/assets/c47260f3-55ca-4e4f-859d-6c51910de147' width='550'>

# Merc Deployer

Here are a list of rigs to download from: https://drive.google.com/drive/u/1/folders/1DF6S3lmqA8xtIMflWhzV242OrUnP62ws

Deploy any of the nine mercs into your scene. You can choose between an advanced rigify (New) rig or a taunt compatible (Legacy) rig. You can read on how to import animations onto a rig in the [Source2Blender](https://source2blender.readthedocs.io/en/latest/TF2Vanilla/Animations.html) docs.

<img src='https://github.com/hisprofile/TF2-Trifecta/assets/41131633/661c0183-3c60-40c0-a73f-10959cc14361' width='400'>

# Bonemerge
Attach cosmetics to a class by choosing a target armature and and selecting the cosmetics to attach.

<img src='https://github.com/user-attachments/assets/d3293c75-f805-4515-88f3-4f0536744b89' width='400'>

You can adjust the influence with the value slider. Influence is added in the order the cosmetics were attached

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

<img src='https://github.com/user-attachments/assets/6541352b-2374-45d0-b6f4-2abe53a1e4fc' height=775>

# End

Thank you Unhelpful Git for coining the name "TF2 Trifecta"
