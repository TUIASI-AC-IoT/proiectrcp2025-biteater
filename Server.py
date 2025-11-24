from DivideFile import divide_file
from ReconstructFile import reconstruct_file

filename= "transmitor.txt"
filename_out="receiver.txt"

packet_list = divide_file(filename)


x = reconstruct_file(packet_list,filename_out)