import os
import sys
import shutil
from rominfo import files, disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images
from romtools.disk import Disk
from romtools.patch import Patch

#DiskAFilename = '46 Okunen Monogatari - The Sinkaron (J) A user.FDI'

#EVODiskAOriginal = Disk(DiskAFilename)
#EVODiskAPatched = Disk
#EVODiskAOriginal.extract('ST1.EXE')

# TODO: Check the extension, and use different 46.EXE patches for the FDI and the HDI.

if __name__ == '__main__':
    if len(sys.argv) < 2:
        #target_diskA = '46 Okunen Monogatari - The Sinkaron (J) A user.FDI'
        #target_diskB2 = '46 Okunen Monogatari - The Sinkaron (J) B 2.FDI'
        #target_diskB3 = '46 Okunen Monogatari - The Sinkaron (J) B 3.FDI'
        #target_diskB4 = '46 Okunen Monogatari - The Sinkaron (J) B 4.FDI'
        target_diskA = '46 Okunen Monogatari - The Shinkaron (Disk 1 - User disk).hdm'
        target_diskB2 = '46 Okunen Monogatari - The Shinkaron (Disk 2).hdm'
        target_diskB3 = '46 Okunen Monogatari - The Shinkaron (Disk 3).hdm'
        target_diskB4 = '46 Okunen Monogatari - The Shinkaron (Disk 4).hdm'
        disks = [target_diskA, target_diskB2, target_diskB3, target_diskB4]
    else:
        target_diskA = sys.argv[1]
        target_diskB2 = sys.argv[2]
        target_diskB3 = sys.argv[3]
        target_diskB4 = sys.argv[4]

    disks = [target_diskA, target_diskB2, target_diskB3, target_diskB4]

    EVODiskAOriginal = Disk(target_diskA)
    print EVODiskAOriginal.extension
    shutil.copyfile(target_diskA, 'backup_' + target_diskA)
    for f in files:
        EVODiskAOriginal.extract(f)
        patch_filename = os.path.join('patch', f + '.xdelta')
        if f == '46.EXE' and EVODiskAOriginal.extension == 'hdi':
            print "It's an HDI, so using a different 46.EXE"
        patchfile = Patch(f, 'edited_' + f, patch_filename)
        patchfile.apply()
        shutil.copyfile('edited_' + f, f)
        EVODiskAOriginal.insert(f)
        os.remove(f)
        os.remove('edited_' + f)

    for i, disk in enumerate([disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images]):
        ImgDisk = Disk(disks[i])
        shutil.copyfile(disks[i], 'backup_' + disks[i])
        for img in disk:
            ImgDisk.extract(img)
            patch_filename = os.path.join('patch', img + '.xdelta')
            patchfile = Patch(img, 'edited_' + img, patch_filename)
            patchfile.apply()
            shutil.copyfile('edited_' + img, img)
            ImgDisk.insert(img)
            os.remove(img)
            os.remove('edited_' + img)

# TODO: Remove the .flp files left behind by patching an .hdm.
# TODO: Apache License v2