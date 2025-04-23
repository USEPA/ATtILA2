#!/bin/bash

## Script to convert ATtILA wiki to html.  
## Clone ATtILA wiki and set parameters below
## Open html in internet browser to make any final edits and export to pdf
## Requires pandoc - tested with v 3.3
## Written for Linux/Bash. Could be configured to run in Windows.


wiki_dir="/data/github/ATtILA2.wiki"
scratch_dir="/data/temp"
sidebar="${wiki_dir}/_Sidebar.md"
attila_version='3.0.1'
output_file="/data/tools/wiki_to_pdf/ATtILA_User_Guide.html"

## organize pages based on _Sidebar.md
count=10
while read line; do
        if [[ ${line} =~ -.* ]]; then
		infile=$(echo $line | sed "s+- \[.*\](<\([^>].*\)>)+\1+")
		outfile=$count-${infile}.md

		## Header is filename with spaces instead of '-'
		## Then we replace the first line in the .md so the header and page name match
		header=$(echo $infile | sed "s%-% %g")
		sed "1 s/^.*$/# ${header}/" ${wiki_dir}/${infile}.md > $scratch_dir/$outfile

		## remove navigation at top of each page for now.  might be able to get this working better with some effort
		sed -i "s:^| \[Summary.*$::" $scratch_dir/$outfile

		## remove navigation at bottom of each page
		sed -i 's/^[![arrow_up].*//' $scratch_dir/$outfile
		#sed -i 's/^[![arrow_up].*/,$d' $scratch_dir/$outfile

		## Change image urls.
		sed -i "s|/USEPA/ATtILA2/wiki/ATtILA2help|${wiki_dir}/ATtILA2help|g" $scratch_dir/$outfile

		## Format image tags for captions
		perl -i -pe 's|!\[Image\]\(<(.*?)>.*?"(.*?)"\)|![$2]($1)|s' $scratch_dir/$outfile

		## Make non http and non-image paths relative 
		perl -i -pe 's%\(<((?!http|/home)[^>]*)>\)%(<#\L\1>)%g' $scratch_dir/$outfile
		#count=$[$count + 1]

		## allow break on underscores.  This helps the tables format correctly
		sed -i 's%\\_%\\_<wbr>%g' $scratch_dir/$outfile

        fi
        count=$[$count + 1]

done < $sidebar

## Use the sidebar as table of contents
cp $sidebar "$scratch_dir/13-aaa_sidebar.md"
perl -i -pe 's%\(<((?!http|/home)[^>]*)>\)%(<#\L\1>)%g' "$scratch_dir/13-aaa_sidebar.md"
sed -i "1s/.*/# Table of Contents/" "$scratch_dir/13-aaa_sidebar.md"

## Remove duplicate header in home
sed -i "2,5d" "$scratch_dir/12-Home.md"
sed -i '1s/.*/<div style="page-break-after:always"><\/div>/' "$scratch_dir/12-Home.md"

## Add custom css file
cat ./custom_style.css > "$scratch_dir/10-css.md"


pandoc --standalone --embed-resources --pdf-engine=xelatex -t html5 -i $(find $scratch_dir -name *.md | sort -n) --metadata subtitle="v${attila_version}  -  " --metadata subtitle="$(date '+%B %d, %Y')" ./metadata.yaml -o ${output_file}

