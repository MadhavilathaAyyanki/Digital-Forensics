
import sys
import struct
import os

class FAT:
    # Initialization and extraction of all the memory attributes of the image file.
    def __init__(self, imgFile: str) -> None:
        self.BytsPerSec = 512
        self.ImagFile = open(imgFile, 'rb')
        # unpacking boot sector variables like BS_jmpBoot, BS_OEMName information from the bytes data
        self.jmpBoot, self.OemName =  struct.unpack('<3s8s', self.fetch_bytes_data(0)[:11])
        # unpacking BIOS Parameter Blocks like BPB_BytsPerSec, BPB_SecPerClus, BPB_RsvdSecCnt, BPB_NumFATs
        # BPB_RootEntCnt, BPB_TotSec16, BPB_Media, BPB_FATSz16, BPB_SecPerTrk, BPB_NumHeads, BPB_HiddSec,
        # BPB_TotSec32 information from the bytes data to navigate through the image data
        self.BytsPerSec, self.Sectors_Per_Cluster, \
            self.ResvdSecCnt, self.NumFATs, self.RootEntCnt, \
            self.TotSec16, self.Media, self.FATSz16, \
            self.SecPerTrk, self.NumHeads, self.HiddSec, \
            self.TotSec32, self.FATSz32 = struct.unpack('<HBHBHHBHHHLLL', \
        self.fetch_bytes_data(0)[11:40])
        
        # creating the required cluster/sector variables to identify the start offset, end offset,
        # Directory location and file locations.
        self.RootDirSectors = int((self.RootEntCnt * 32 + \
            self.BytsPerSec - 1) /self.BytsPerSec)
        self.DataSec = self.TotSec16 - (self.ResvdSecCnt \
            +(self.NumFATs * self.FATSz16) + self.RootDirSectors)
        self.FATStart = self.ResvdSecCnt
        self.CountOfClusters = int(self.DataSec / self.Sectors_Per_Cluster)
        self.DatSecFrst = self.ResvdSecCnt + (self.NumFATs * self.FATSz16) + \
            self.RootDirSectors
        self.RootDirStart = self.ResvdSecCnt + self.NumFATs * self.FATSz16
        
    def __str__( self ) -> str :
        return '\nBytsPerSec = {} bytes\nSectors_Per_Cluster = {} sectors\nResvdSecCnt = {} sectors\nNumFATs = {}\nRootEntCnt = {} entries\nTotSec16 = {} sectors\nFATSz16 = {} sectors\nHiddSec = {} sectors\n\n'.format(
        self.BytsPerSec,
        self.Sectors_Per_Cluster,
        self.ResvdSecCnt,
        self.NumFATs,
        self.RootEntCnt,
        self.TotSec16,
        self.FATSz16,
        self.HiddSec
    )           

    # Read the contents of the current cluster and return the offset for next cluster
    def get_fat_offset_data(self, cluster):
        fat_sector_number = self.FATStart + \
            (cluster // 256)
        fat_sector = self.fetch_bytes_data(fat_sector_number)
        entry_offset = cluster % 256
        # the offset values are obtained by unpacking the cluster bytes
        next_cluster = struct.unpack("<H", \
            fat_sector[entry_offset * 2:entry_offset * 2 + 2])[0]
        return next_cluster

    # close the opened image file once the data is parsed 
    # and all navigation operations are completed
    def close(self) -> None:
        self.ImagFile.close()

    # The below function fetch_bytes_data() returns specific number of bytes starting from specific sector
    # the number of bytes is obtained by using the BPB_BytsPerSec value
    def fetch_bytes_data(self, sector: int) -> bytes:
        self.ImagFile.seek(sector * self.BytsPerSec)
        return self.ImagFile.read(self.BytsPerSec)

    # The below function search_files_folders() identify the files and folders in the image
    def search_files_folders(self):
        if True:
            data_root_direct = self.fetch_bytes_data(self.RootDirStart)
            is_root_direct_empty = not any(data_root_direct)

        # if the root directory is not found, check for files
        if bool(is_root_direct_empty):
            file_counter = 0
            print()
            print("Directory found at the below clusters:")
            length = 1
            with open("GoodFiles/listing.txt","w") as files_list:
             for val_cluster in range(2, self.CountOfClusters):
                if True:
                    sec_per_cluser = (val_cluster - 2) * self.Sectors_Per_Cluster
                    sec_strt = self.DatSecFrst + sec_per_cluser

                if True:
                    offset_sec_data = self.fetch_bytes_data(sec_strt)

                # if the fist byte and eleventh byte is related to partition, print them
                if all([offset_sec_data[0] == 0x2E,offset_sec_data[11] == 0x10]):
                    data_clus = bytes()
                    # directory found
                    print(f"Cluster {val_cluster}") 
                    
                    if True:
                        # calculating total number of sectors allocated/occupied by the clusters
                        # and calculating current cluster's starting sector number
                        clus_sec_perClus = (val_cluster - 2) * self.Sectors_Per_Cluster
                        sec_st_dir = self.DatSecFrst + clus_sec_perClus
                        
                    # with in the current cluster, loop through each sector
                    for eleSectors_Per_Cluster in range(0, self.Sectors_Per_Cluster):
                        # Fetch the sector's data and and add it to the cluster's current data
                        data_clus = data_clus + self.fetch_bytes_data(sec_st_dir + eleSectors_Per_Cluster)
                    
                    if True:
                        data_directory = data_clus
                    
                    # creating a string v1 which indicates the the clluster that is currently being processed 
                    # and write it to the files_list
                    v1=f"Folder/Directory at cluster {val_cluster}:\n"
                    files_list.write(v1)

                    # parse the directory list with jump value of 32 and check for file marker
                    for dt_dir in range(0, len(data_directory), 32):
                        if True:
                            start_line = data_directory[dt_dir:dt_dir+32]
                        if any([start_line[0] == 0x00,start_line[0] == 0xE5]):
                            continue 
                        
                        # if the 11 bit of start_line is not 10, it is not a directory, so 
                        # unpack the file attributes like starting_cluster, 
                        # file_size, file_name from the respective byte locations
                        if not (start_line[11] == 0x10): 
                            file_var = f"FILE{length:04d}"
                            if True:
                                starting_cluster = struct.unpack("<H", start_line[26:28])[0]

                            if True:
                                file_size = struct.unpack("<L", start_line[28:32])

                            if True:
                                file_name = struct.unpack("<8s3s", start_line[:11])
                            
                            # The content of the found files will be read and 
                            # saved in listing text file along with the file attributes
                            # if the 11 bit of start_line is 20, increment the file_counter and
                            # write the file_type, file_name and size of the file information to the files_list
                            if start_line[11] == 0x20:
                                file_counter += 1
                                good_files = []
                                files_list.write(f"GoodFile: {file_name[0].decode('ascii').strip()} - Length: {file_size[0]}\n")
                                good_files.append(file_name[0].decode('ascii').strip())
                                length = length + 1
                                data_file = bytes()
                                current_cluster = starting_cluster
                                # Clusters should be read until end-of-chain marker
                                while current_cluster < 0xFFF0:  
                                    current_sector = self.DatSecFrst + (current_cluster - 2) * \
                                        self.Sectors_Per_Cluster
                                    
                                    # Using the Sectors_Per_Cluster value fetch all 
                                    # the bytes and store them in a variable.
                                    for i in range(self.Sectors_Per_Cluster):
                                        inter_val = current_sector + i
                                        data_file = data_file + self.fetch_bytes_data(inter_val)
                                        
                                    if True:
                                        current_cluster = self.get_fat_offset_data(current_cluster) 
                                
                                # write all the bin files to the relevant file names 
                                # and store them in RecoveredFiles as .bin files
                                if True:
                                    with open(f"RecoveredFiles/{file_var}.bin", "wb") as bin_file:
                                        bin_file.write(data_file) # bin files creation
                                
                                # Trim the unwanted bits to get the actual file size
                                data_file = data_file[:file_size[0]]
                                
                                # write all the trimmed text files to the relevant file names 
                                # and store them in RecoveredFiles as .txt files
                                with open(f"RecoveredFiles/{file_var}.txt", \
                                    "wb") as text_file:
                                    text_file.write(data_file) # txt files creation
                                    
                                # write all the good files to the relevant file names 
                                # and store them in GoodFiles directory as .txt files
                                with open(f"GoodFiles/{good_files[0]}.txt", "wb") as store_good_file:
                                     store_good_file.write(data_file) # txt files creation 
                            else:
                                continue
            print()
            # based on the file_counter value , print the total files found in the image
            print("Total GoodFiles found are",file_counter)
            print()
            
    # The below function _unlinked_() is used to get the unlinked files present in each cluster       
    def _unlinked_(self):
        for val_cluster in range(2, self.CountOfClusters):
                    sec_per_cluser = (val_cluster - 2) * self.Sectors_Per_Cluster
                    sec_strt = self.DatSecFrst + sec_per_cluser
                    sec_dat = self.get_fat_offset_data(sec_strt)
                    clus_dat = self.file_info(sec_strt)
                    # parse the directory list with jump value of 32 and check for file marker
                    for dt_dir in range(0, len(clus_dat), 32):
                            start_line = clus_dat[dt_dir:dt_dir+32]
                    if (start_line[0] == 0xE5):
                            continue 

if __name__ == "__main__":
    # create GoodFiles folder if it does not 
    # exist, and store the listing.txt file to the GoodFiles folder
    curr_path=os.getcwd()
    new_fol="GoodFiles"
    if os.path.exists(curr_path+"/"+new_fol) == False:
        os.mkdir(curr_path+"/"+new_fol)

    # create RecoveredFiles folder if it does not 
    # exist, and store the recovered bin and txt files to the RecoveredFiles
    RecoveredFiles="RecoveredFiles"
    if os.path.exists(curr_path+"/"+RecoveredFiles) == False:
        os.mkdir(curr_path+"/"+RecoveredFiles)
    
    img_file = FAT(r"/home/ayyankid/h-drive/443 digital forensics/python coursework/final code/case=36269348/fat16-36269348-13.img")
    print(img_file)
    # call the search_files_folders function from FAT 
    # class to invoke the search operation
    img_file.search_files_folders()
    img_file.close()
    
