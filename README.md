# Dynamic Tournament Slideshow

This slideshow automatically detects pictures in the `/pictures` folder and creates slides for them. It checks every 15 seconds for new pictures and updates the slideshow dynamically.

## Quick Start

### Option 1: With Server (Recommended)
1. **Start the server:**
   ```bash
   cd tournament_screens
   python3 server.py
   ```
2. **Open in browser:** http://localhost:8000
3. **Add pictures:** Drop any images into the `pictures/` folder
4. **Watch magic happen:** New slides appear automatically every 15 seconds!

### Option 2: File-based (Simple)
1. **Open `index.html`** directly in your browser
2. **Add pictures** to the `pictures/` folder with names:
   - `picture1.jpg`, `picture2.jpg`, `picture3.jpg`, etc.
3. **Refresh page** to see new pictures

## Features

✅ **Auto-discovery** - Finds all pictures in the pictures folder  
✅ **Live updates** - Checks every 15 seconds for changes  
✅ **Dynamic slides** - Adds/removes slides automatically  
✅ **Countdown timer** - Shows round countdown at the top  
✅ **Fullscreen ready** - Perfect for projectors  
✅ **Multiple formats** - Supports JPG, PNG, GIF, WebP, BMP  

## How It Works

1. **Scans pictures folder** every 15 seconds
2. **Creates slides** for each image found
3. **Adds info slide** showing picture count
4. **Rotates through slides** every 5 seconds
5. **Updates automatically** when pictures change

## Folder Structure
```
tournament_screens/
├── index.html          # Main slideshow page
├── server.py           # Optional server for auto-discovery
├── pictures/           # Put your images here!
│   ├── picture1.jpg
│   ├── picture2.png
│   └── ...
└── README.md          # This file
```

## Tips

- **Picture names don't matter** when using the server
- **Any image format** works (JPG, PNG, GIF, etc.)
- **Large images** are automatically resized to fit
- **Add/remove pictures** anytime - they appear within 15 seconds
- **Perfect for live events** - update pictures during the tournament!

## Troubleshooting

**Pictures not showing?**
- Check the `pictures/` folder exists
- Ensure images have proper extensions (.jpg, .png, etc.)
- Try refreshing the page

**Using without server?**
- Name pictures: `picture1.jpg`, `picture2.jpg`, etc.
- Update the `pictureNames` array in the HTML if needed

**Want different timing?**
- **Slide duration:** Change `5000` in `setInterval(nextSlide, 5000)`
- **Check interval:** Change `15000` in `setInterval(updateSlides, 15000)`
