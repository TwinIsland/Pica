# Pica
hide text into image

![](pica.png)
## Usage
```
Encrypt/decrypt text into/from an image.

options:
  -h, --help            show this help message and exit
  -i, --image IMAGE     Path to the image file
  -e, --encrypt [ENCRYPT]
                        Encrypt text into the image (optional input text)
  -d, --decrypt         Decrypt text from the image
```

## Examples
**Text to Image:**
```
python .\pica.py -i .\pica.png -e "hello world"
```

**Image to Text:**
```
python .\pica.py -i .\pica.png -d
```

**Use piping :**
```
cat .\readme.md | python .\pica.py -i .\pica.png -e
```