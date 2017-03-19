from os import path, remove
from shutil import copyfile
from rominfo import files, disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images
from romtools.disk import Disk
from romtools.patch import Patch, PatchChecksumError

def patch(diskA, diskB2=None, diskB3=None, diskB4=None, path_in_disk=None):
    # HDIs just have the one disk, received as the arg diskA.
    if not diskB2 and not diskB3 and not diskB4:
        disks = [diskA, diskA, diskA, diskA]
    elif diskB2 and diskB3 and diskB4:
        disks = [diskA, diskB2, diskB3, diskB4]
    else:
        raise Exception # TODO: Gotta be something better than this

    # TODO: Use FILES_TO_PATCH to avoid separate loops for the A disk and the images.

    EVODiskAOriginal = Disk(diskA)
    EVODiskAOriginal.backup()
    for f in files:
        print path_in_disk
        EVODiskAOriginal.extract(f, path_in_disk)
        if f == '46.EXE' and EVODiskAOriginal.extension == 'hdi':
            print "It's an HDI, so using a different 46.EXE"
            patch_filename = path.join('patch', 'HDI_46.EXE.xdelta')
        else:
            patch_filename = path.join('patch', f + '.xdelta')
        patchfile = Patch(f, f + '_edited', patch_filename)

        try:
            patchfile.apply()
        except PatchChecksumError:
            print "Exception raised while trying to patch file", f

        # TODO: What to do if the checksum fails? Should we patch the other files?

        try:
            copyfile(f + '_edited', f)
        except IOError:
            print "One of the patches didn't work. Restoring the disk from backup..."
            EVODiskAOriginal.restore_from_backup()
            return "Checksum error in file " + f

        EVODiskAOriginal.insert(f, path_in_disk)
        remove(f)
        remove(f + '_edited')

    for i, disk in enumerate([disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images]):
        ImgDisk = Disk(disks[i])

        # For HDIs, don't backup the disk again - this would leave users with a mostly-patched backup
        if disks[i] != diskA:
            ImgDisk.backup()
        for img in disk:
            ImgDisk.extract(img, path_in_disk)
            patch_filename = path.join('patch', img + '.xdelta')
            patchfile = Patch(img, img + '_edited', patch_filename)
            try:
                patchfile.apply()
            except PatchChecksumError:
                print "Exception raised while trying to patch file", f

            copyfile(img + '_edited', img)
            ImgDisk.insert(img, path_in_disk)
            remove(img)
            remove(img + '_edited')

    return None

# TODO: Use a generator to feed progress to the console in the GUI.
# TODO: Apache License v2 due to xdelta

if __name__ == '__main__':
    patch('46 Okunen Monogatari - The Shinkaron.hdi')