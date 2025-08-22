image_capured = 1
while image_capured < 15:

    move, scan = useVisualMicroscope()
    
    if move:
        preformMovement()

    if scan:
        preformScanAndSave()

    image_capured + 1