import nanosurf as nsf

spm = nsf.SPM()

print(spm.is_connected())

cameras = spm.application.Video



cameras.VideoSource = 1
if cameras.SaveFrame("topimage.jpg") == False:
    print( "Could not save video image!")


