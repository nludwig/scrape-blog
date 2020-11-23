# scrape-blog
Grab simply formatted blog content and format it as a `.docx` for eventual upload to ereader.
In particular, as of 201122, designed to scrape [SSC](https://slatestarcodex.com/).

## Usage example
First, clone the repo locally:
```
git clone https://github.com/nludwig/scrape-blog.git
```

Next, install the required Python dependencies:
```
cd scrape-blog
pip3 install -r requirements.txt
```

To make a `.docx` file containing one years worth of SSC, say 2013, use the command
```
year=2013 && scrape_blog/scrape_ssc.py --out ssc${year}.docx --test False -r $year --title "Slate Star Codex, $year"
```

The output, `ssc2013.docx`, can be read directly on a computer or an ereader
(for example, it can be uploaded to a Kindle using your 
[Send to Kindle email](https://www.amazon.com/gp/sendtokindle/email)
).
Alternatively, additional formatting can be done first, for example, adding
a navigable table of contents.
I accomplished that further formatting by:
1. Importing the `.docx` file into Amazon's
   [Kindle Create](https://www.amazon.com/Kindle-Create/b?node=18292298011)
   application (I used Windows for this).
   (NOTE: This step may not be necessary; simply loading
   the `.docx` file into Calibre may be enough).
1. After saving the project, creating a `.kpf` file.
1. Load the `.kpf` file into
   [Calibre](https://calibre-ebook.com/)
   and convert to a `.mobi` file.

You can find the results of a scrape I performed on
201122 in this repo in the 201122-ssc directory. 
