from os import path, remove
from shutil import copyfile
from rominfo import files, disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images
from romtools.disk import Disk, FileNotFoundError, UnicodePathError, HARD_DISK_FORMATS
from romtools.patch import Patch, PatchChecksumError

def patch(diskA, diskB2=None, diskB3=None, diskB4=None, path_in_disk=None, backup_folder='./backup'):
    # HDIs just have the one disk, received as the arg diskA.
    if not diskB2 and not diskB3 and not diskB4:
        disks = [diskA, diskA, diskA, diskA]
    elif diskB2 and diskB3 and diskB4:
        disks = [diskA, diskB2, diskB3, diskB4]
    else:
        raise Exception # TODO: Gotta be something better than this

    EVODiskAOriginal = Disk(diskA, backup_folder=backup_folder)
    EVODiskAOriginal.backup()

    diskA_dir = path.dirname(diskA)

    disk_format = diskA.split('.')[-1].lower()

    if disk_format == 'd88':
        print disks
        for d in disks:
            D88Disk = Disk(d, backup_folder=backup_folder)
            D88Disk.backup()
            disk_name = path.basename(d)
            patch_filename = path.join('patch', disk_name + '.xdelta')
            patchfile = Patch(d, patch_filename)
            try:
                patchfile.apply()
            except PatchChecksumError:
                return "Checksum error in disk %s." % d

        return None

    for f in files:
        try:
            EVODiskAOriginal.extract(f, path_in_disk)
        except FileNotFoundError:
            EVODiskAOriginal.restore_from_backup()
            return "File %s not found in disk.\nTry setting the path under 'Advanced'." % f
        except UnicodePathError:
            # TODO: Try writing the command to a batch file, then running that.
            with open('test.bat', 'w') as bat:
                bat.write(cmd)

            return "Patching in paths containing non-ASCII characters not supported."

        if f == '46.EXE' and EVODiskAOriginal.extension.lower() in HARD_DISK_FORMATS:
            print "It's an HDI, so using a different 46.EXE"
            patch_filename = path.join('patch', 'HDI_46.EXE.xdelta')
        else:
            patch_filename = path.join('patch', f + '.xdelta')

        extracted_file_path = diskA_dir + '/' + f

        copyfile(extracted_file_path, extracted_file_path + '_edited')
        patchfile = Patch(extracted_file_path, patch_filename, edited=extracted_file_path + '_edited')

        try:
            patchfile.apply()
        except PatchChecksumError:
            EVODiskAOriginal.restore_from_backup()
            remove(extracted_file_path)
            remove(extracted_file_path + '_edited')
            return "Checksum error in file %s." % f

        copyfile(extracted_file_path + '_edited', extracted_file_path)

        EVODiskAOriginal.insert(extracted_file_path, path_in_disk)
        remove(extracted_file_path)
        remove(extracted_file_path + '_edited')

    for i, disk in enumerate([disk_a_images, disk_b2_images, disk_b3_images, disk_b4_images]):
        ImgDisk = Disk(disks[i], backup_folder=backup_folder)
        imgdisk_dir = path.dirname(disks[i])

        # For HDIs, don't backup the disk again - this would leave users with a mostly-patched backup
        if disks[i] != diskA:
            ImgDisk.backup()
        for img in disk:
            try:
                ImgDisk.extract(img, path_in_disk)
            except FileNotFoundError:
                ImgDisk.restore_from_backup()
                return "File %s not found in disk." % img

            extracted_file_path = imgdisk_dir + '/' + img
                
            patch_filename = path.join('patch', img + '.xdelta')
            copyfile(extracted_file_path, extracted_file_path + '_edited')
            patchfile = Patch(extracted_file_path, patch_filename, edited=extracted_file_path + '_edited',)

            try:
                patchfile.apply()
            except PatchChecksumError:
                ImgDisk.restore_from_backup()
                remove(extracted_file_path)
                remove(extracted_file_path + '_edited')
                return "Checksum error in file %s." % img

            copyfile(extracted_file_path + '_edited', extracted_file_path)
            # Can't use extracted_file_path, since it also tries to delete the path in the disk...
            ImgDisk.insert(extracted_file_path, path_in_disk)
            remove(extracted_file_path)
            remove(extracted_file_path + '_edited')

    return None

# TODO: Apache License v2 due to xdelta

if __name__ == '__main__':
    patch('46 Okunen Monogatari - The Shinkaron.hdi')
