import os
import sys
import shutil
from rominfo import files, disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images
from romtools.disk import Disk
from romtools.patch import Patch

def patch(diskA, diskB2=None, diskB3=None, diskB4=None):
    # HDIs just have the one disk, received as the arg diskA.
    if not diskB2 and not diskB3 and not diskB4:
        disks = [diskA, diskA, diskA, diskA]
    elif diskB2 and diskB3 and diskB4:
        disks = [diskA, diskB2, diskB3, diskB4]
    else:
        raise Exception

    EVODiskAOriginal = Disk(diskA)
    diskA_backup = '/'.join(diskA.split('/')[:-1]) + "/backup_" + diskA.split('/')[-1]
    shutil.copyfile(diskA, diskA_backup)
    for f in files:
        EVODiskAOriginal.extract(f)
        if f == '46.EXE' and EVODiskAOriginal.extension == 'hdi':
            print "It's an HDI, so using a different 46.EXE"
            patch_filename = os.path.join('patch', 'HDI_46.EXE.xdelta')
        else:
            patch_filename = os.path.join('patch', f + '.xdelta')
        print patch_filename
        patchfile = Patch(f, f + '_edited', patch_filename)
        patchfile.apply()

        # TODO: Can't really detect exceptions in the xdelta thing yet, that'd be good to do.

        try:
            shutil.copyfile(f + '_edited', f)
        except IOError:
            print "One of the patches didn't work. Restoring the disk from backup"
            shutil.copyfile(diskA_backup, diskA)
            os.remove(diskA_backup)
            return False

        EVODiskAOriginal.insert(f)
        os.remove(f)
        os.remove(f + '_edited')

    for i, disk in enumerate([disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images]):
        ImgDisk = Disk(disks[i])
        img_backup = '/'.join(disks[i].split('/')[:-1]) + "/backup_" + disks[i].split('/')[-1]
        shutil.copyfile(disks[i], img_backup)
        for img in disk:
            ImgDisk.extract(img)
            patch_filename = os.path.join('patch', img + '.xdelta')
            patchfile = Patch(img, img + '_edited', patch_filename)
            patchfile.apply()
            shutil.copyfile(img + '_edited', img)
            ImgDisk.insert(img)
            os.remove(img)
            os.remove(img + '_edited')

    # Cleanup any leftover .flp files, if it was an .hdm
    for d in disks:
        if d.split('.')[-1].lower() == 'hdm':
            flp_filename = '.'.join(d.split('.')[:-1]) + '.flp'
            os.remove(flp_filename)

    return True

# TODO: Use a generator to feed progress to the console in the GUI.
# TODO: Apache License v2 due to xdelta
# TODO: Why are the backups of the HDM getting edited??

#if __name__ == '__main__':
#    patch()