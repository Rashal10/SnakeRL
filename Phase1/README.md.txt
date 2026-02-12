# 🐍 Drake's Snake Game (Pygame)

A fun little **Snake Game** built with **Python** and **Pygame**.  
Unlike the classic rectangle-only snake, this version uses a apple 🍎 as the favorite food of the circle ball shaped snake.  

---

## 🎮 Features
- Classic Snake gameplay
- Food is represented with a **custom apple image** (`apple.png`)
- Simple, beginner-friendly codebase
- Current Score, Level and Highest Score is available
- Play-again / quit option after game over

---

## 🖼️ Project Structure
```

Snake Game
├── Snake.py
├── apple.png
├── screenshot.png   
└── README.md

```

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/snake-game.git
cd snake-game
```

### 2. Install Dependencies
Make sure you have Python installed (3.8+ recommended).  
Install **pygame**:
```bash
pip install pygame
```

### 3. Run the Game

Firstly, Make sure you are in the folder of the game.

```bash
python Snake.py
```

---

## 🎮 Controls
- ⬆️ **Arrow Up** → Move up  
- ⬇️ **Arrow Down** → Move down  
- ⬅️ **Arrow Left** → Move left  
- ➡️ **Arrow Right** → Move right  

---

## 🔧 Customization
- Replace `apple.png` with any other 20×20 (or rescaled) image to change the food.  
- Adjust the snake speed by modifying `clock.tick(10)` inside `Snake.py`.  
- Add your own images for the snake body (currently drawn with a simple block).  

---

## 📸 Preview
*(Add a screenshot or GIF of gameplay here, e.g., `screenshot.png`)*  
```bash
![Snake Game Demo](./screenshot.png)
```

---

## 🤝 Contributing
Want to improve the game? Well I really appreciate it.
Please add a better image of the snake. 

Pull requests are welcome 

---

## 📜 License
This project is open-source under the **MIT License**.  
You’re free to use, modify, and share it.  

---

### 👨‍💻 Author
Made with ❤️ using Python and [Pygame](https://www.pygame.org/news).
