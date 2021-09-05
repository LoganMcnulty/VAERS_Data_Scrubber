# VAERS_Data_Scrubber
Scrubbed VAERS Covid-19 data into pandas dateframe. Over 500k unique records. 

NOTE: if pd.read_csv(filePath) throws an error, open the source .csv files, and save them. Doing this alleviates the bug, not sure why. Passing encoding param didn't work. 

https://vaers.hhs.gov/data.html

To run the script
- Download/ fork repo 
- Check the package requirements
- Download the files in the link
- Update the file paths
- Run the whole thing
