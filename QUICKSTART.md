# 🚀 NextAstroTarget - Quick Reference Guide

## Starting the Application

### Option 1: Desktop Shortcut (Easiest)
- Double-click the **NextAstroTarget** icon on your desktop
- Shortcut includes the telescope icon

### Option 2: Batch File
- Navigate to the application folder
- Double-click `NextAstroTarget.bat`

### Option 3: Command Line
```powershell
cd D:\REPOS\NextAstroTarget
python main_pyside6.py
```

---

## Creating/Recreating Desktop Shortcut

If you need to create or recreate the desktop shortcut:

```powershell
python create_desktop_shortcut.py
```

This will create a shortcut with:
- ✓ Application icon (telescope)
- ✓ Correct working directory
- ✓ Proper Python environment
- ✓ Description tooltip

---

## Main Features Overview

### 1. Filter Panel (Left Side)
- **Rating**: ⭐ Filter by object rating (3+, 4+, 5)
- **Type**: Galaxies, Nebulae, Clusters, Others
- **Size Range**: Filter by object size in arcminutes
- **Transit Time**: Show objects transiting in time window
- **🔄 Clear All Filters**: Reset all filters

### 2. Search Bar (Top)
- Search by object name
- Catalog numbers: M31, NGC 7000, IC 434
- Fuzzy matching for partial names
- **🧹 Clear** button to reset search

### 3. Object Table (Center)
- Click column headers to sort
- Hover over objects for quick preview
- **Double-click** to see detailed view with sky image

### 4. Information Panels (Right Side)

#### ☀️ Sun & 🌙 Moon
- Current altitude and azimuth
- Rise/set times
- Nautical twilight times
- Moon phase visualization

#### 🌤️ Weather Forecast
- ClearOutside astronomical forecast
- Updated automatically on startup
- Click refresh to update

---

## Sky Survey Images

When you double-click an object, you see:

### Image Sources
1. **SDSS (Primary)**: Sloan Digital Sky Survey
   - High-quality color CCD images
   - Best for galaxies and extragalactic objects
   - Modern data from 2000s

2. **DSS (Fallback)**: Digitized Sky Survey
   - RGB color composite from Red + Blue filters
   - Complete sky coverage
   - Works for all objects including Milky Way nebulae

### Image Quality
- **Automatic selection**: SDSS tried first, DSS if unavailable
- **Color images**: Both sources provide color
- **Field of view**: SDSS 3.4', DSS 15' (wider field)

---

## Configuration

### Observatory Location
Edit `config/config.ini`:

```ini
[Observatory]
latitude = 54.38
longitude = 18.49
elevation = 100.0
gmt_offset = 1.0
dst_active = false
timezone = CET
```

### Database
- Location: `data/astro_targets.db`
- Contains 3139+ deep-sky objects
- Automatically created on first run

---

## Tips & Tricks

### Finding Objects
1. Use **Rating 5** + **Type filter** for best targets
2. **Search**: "M31" finds Andromeda Galaxy
3. **Transit filter**: Find objects overhead tonight

### Best Practices
- Check sun/moon times before observing
- Use weather forecast for cloud predictions
- Filter by size to match your field of view

### Performance
- Sky images are **cached** automatically
- First load may be slower (downloading)
- Subsequent views are instant

---

## Troubleshooting

### Desktop shortcut not working?
```powershell
python create_desktop_shortcut.py
```

### Application won't start?
Check Python is installed:
```powershell
python --version
```

### Missing images?
- Check internet connection
- Images download on-demand
- DSS/SDSS servers may be temporarily slow

### Database issues?
- Database auto-creates on first run
- Located at: `data/astro_targets.db`
- Delete and restart to rebuild

---

## Keyboard Shortcuts

- **Ctrl+F**: Focus search box (when implemented)
- **Escape**: Close dialog windows
- **Double-click**: Open object details

---

## Support

For issues or questions:
- GitHub: https://github.com/tonagruzu/NextAstroTarget
- Check logs: `logs/nextastrotarget.log`

---

**Version**: 2.0.0 (PySide6)  
**Last Updated**: November 2025
