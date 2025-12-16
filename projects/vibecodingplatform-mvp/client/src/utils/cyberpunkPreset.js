/**
 * Cyberpunk 赛博朋克风格预设
 * 包含强制使用的配置文件和 UI 组件，确保所有生成的应用都拥有统一的未来科技感
 */

const PACKAGE_JSON = {
  name: "cyberpunk-app",
  private: true,
  version: "0.0.0",
  type: "module",
  scripts: {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  dependencies: {
    "@radix-ui/react-slot": "^1.0.2",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "framer-motion": "^11.0.8",
    "lucide-react": "^0.344.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.3",
    "tailwind-merge": "^2.2.1",
    "tailwindcss-animate": "^1.0.7"
  },
  devDependencies: {
    "@types/react": "^18.2.64",
    "@types/react-dom": "^18.2.21",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.18",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.2.2",
    "vite": "^5.1.6"
  }
};

const TAILWIND_CONFIG = `/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "scale-pop": {
          "0%": { transform: "scale(1)" },
          "50%": { transform: "scale(1.05)" },
          "100%": { transform: "scale(1)" },
        },
        "pulse-glow": {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        "shimmer": {
          "0%": { backgroundPosition: "-200% center" },
          "100%": { backgroundPosition: "200% center" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fade-in": "fade-in 0.5s ease-out",
        "scale-pop": "scale-pop 0.3s ease-out",
        "pulse-glow": "pulse-glow 3s ease-in-out infinite",
        "shimmer": "shimmer 3s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}`;

const INDEX_CSS = `@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* === 主题变量（由平台动态注入） === */
    /* 这些变量会被 theme.js 在运行时覆盖，这里只是默认值（青绿主题） */
    --brand1: 174 72% 56%;
    --brand2: 180 60% 40%;
    --glow: 174 72% 50%;
    --bg: 222 84% 5%;
    --card: 220 18% 14%;
    --ring: 174 72% 50%;
    --border: 220 15% 22%;
    --gradient-start: 174 72% 45%;
    --gradient-end: 180 60% 40%;
    
    /* === Cyberpunk 深色主题固定变量 === */
    --background: var(--bg);
    --foreground: 210 40% 98%;
    
    --card: var(--card);
    --card-foreground: 210 40% 98%;
    
    --popover: 220 18% 14%;
    --popover-foreground: 210 40% 98%;
    
    /* 使用品牌色作为主色 */
    --primary: var(--brand1);
    --primary-foreground: 220 20% 10%;
    
    --secondary: 220 18% 18%;
    --secondary-foreground: 210 20% 95%;
    
    --muted: 220 15% 20%;
    --muted-foreground: 215 15% 55%;
    
    --accent: var(--brand1);
    --accent-foreground: 220 20% 10%;
    
    --destructive: 0 72% 55%;
    --destructive-foreground: 210 20% 95%;
    
    --border: var(--border);
    --input: 220 15% 22%;
    --ring: var(--ring);
    
    --radius: 1rem;
    
    /* 保留旧名称作为别名（兼容性） */
    --glow-color: var(--glow);
    --gradient-start: var(--gradient-start);
    --gradient-end: var(--gradient-end);
    
    --font-display: 'Space Grotesk', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  
  body {
    @apply bg-background text-foreground antialiased;
    font-family: var(--font-display);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-display);
  }
}

@layer utilities {
  /* === 通用炫酷样式类（使用 CSS 变量） === */
  
  /* 渐变文字 - 使用品牌色 */
  .text-gradient {
    background: linear-gradient(
      135deg,
      hsl(var(--brand1)) 0%,
      hsl(var(--brand2)) 100%
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  /* 径向渐变背景 - 使用光晕色 */
  .bg-gradient-radial {
    background: radial-gradient(
      ellipse at center,
      hsl(var(--glow) / 0.15) 0%,
      transparent 70%
    );
  }
  
  /* 主色光晕 - 使用光晕色变量 */
  .glow-primary {
    box-shadow: 
      0 0 20px hsl(var(--glow) / 0.3),
      0 0 40px hsl(var(--glow) / 0.2),
      0 0 60px hsl(var(--glow) / 0.1);
  }
  
  /* 玻璃拟态面板 - 使用卡片色 */
  .glass-panel {
    @apply bg-card/80 backdrop-blur-xl border border-border rounded-2xl shadow-2xl;
    background: linear-gradient(
      180deg,
      hsl(var(--card)) 0%,
      hsl(220 18% 12%) 100%
    );
  }
  
  /* Surface 卡片（别名） */
  .surface-card {
    @apply glass-panel;
  }
  
  /* 品牌按钮 - 圆形霓虹风格，使用渐变变量 */
  .btn-brand {
    @apply relative overflow-hidden rounded-full transition-all duration-300 ease-out;
    background: linear-gradient(
      135deg,
      hsl(var(--brand1)) 0%,
      hsl(var(--brand2)) 100%
    );
    box-shadow: 0 0 20px hsl(var(--glow) / 0.4);
  }
  
  .btn-brand:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px hsl(var(--glow) / 0.6);
  }
  
  .btn-brand:active {
    transform: scale(0.95);
  }
  
  /* 品牌轮廓按钮 */
  .btn-brand-outline {
    @apply relative overflow-hidden rounded-full border-2 bg-transparent transition-all duration-300 ease-out;
    border-color: hsl(var(--brand1) / 0.5);
    color: hsl(var(--brand1));
  }
  
  .btn-brand-outline:hover {
    border-color: hsl(var(--brand1));
    background: hsl(var(--brand1) / 0.1);
    box-shadow: 0 0 20px hsl(var(--glow) / 0.3);
  }
  
  .btn-brand-outline:active {
    transform: scale(0.95);
  }
}
`;

// UI Components
const BUTTON_TSX = `import * as React from "react"
import { cva } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md font-medium ring-offset-background transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90 hover:shadow-lg shadow-sm",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-sm",
        outline: "border border-border bg-transparent text-foreground hover:bg-secondary hover:border-primary/50",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-secondary hover:text-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        hero: "bg-primary text-primary-foreground font-semibold shadow-lg hover:shadow-[0_0_30px_hsl(var(--primary)/0.5)] hover:scale-105 transition-all duration-300",
        heroOutline: "border-2 border-primary/60 bg-transparent text-foreground hover:bg-primary/10 hover:border-primary font-semibold transition-all duration-300",
      },
      size: {
        default: "h-10 px-4 py-2 text-sm",
        sm: "h-9 rounded-md px-3 text-sm",
        lg: "h-12 rounded-lg px-8 text-base",
        xl: "h-14 rounded-lg px-10 text-lg",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const Button = React.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"

export { Button, buttonVariants }
`;

const INPUT_TSX = `import * as React from "react"

import { cn } from "@/lib/utils"

const Input = React.forwardRef(({ className, type, ...props }, ref) => {
  return (
    <input
      type={type}
      className={cn(
        "flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lovable-orange focus-visible:border-transparent disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Input.displayName = "Input"

export { Input }
`;

const CARD_TSX = `import * as React from "react"

import { cn } from "@/lib/utils"

const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-2xl border border-border bg-card text-card-foreground shadow-card hover:shadow-hover transition-all duration-300",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-8", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-display font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-8 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-8 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
`;

const APP_SHELL_TSX = `import React from 'react';
import { motion } from 'framer-motion';

/**
 * AppShell - 全局应用容器
 * 提供统一的深色背景、网格纹理和光晕效果
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen w-full bg-background relative overflow-hidden">
      {/* 背景光效层 */}
      <div className="fixed inset-0 pointer-events-none">
        {/* 左上角光晕 */}
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[120px] animate-pulse-glow" />
        
        {/* 右下角光晕 */}
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-500/5 blur-[120px] animate-pulse-glow" style={{ animationDelay: '1.5s' }} />
        
        {/* 网格纹理 */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
      </div>

      {/* 主内容容器 */}
      <main className="relative z-10 container mx-auto px-4 py-8 flex flex-col items-center justify-center min-h-screen">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="w-full max-w-5xl"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
`;

const UTILS_TS = `import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
`;

const VITE_CONFIG = `import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
`;

const TSCONFIG_JSON = JSON.stringify({
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}, null, 2);

const TSCONFIG_NODE_JSON = JSON.stringify({
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}, null, 2);

const POSTCSS_CONFIG = `export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
`;

const INDEX_HTML = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Cyberpunk App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
`;

const MAIN_TSX = `import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
`;

/**
 * 基础预设文件映射
 * 这些文件会被强制注入到每个生成的项目中，AI 无法修改
 */
export const BASE_PRESET_FILES = {
  'package.json': JSON.stringify(PACKAGE_JSON, null, 2),
  'tsconfig.json': TSCONFIG_JSON,
  'tsconfig.node.json': TSCONFIG_NODE_JSON,
  'vite.config.ts': VITE_CONFIG,
  'postcss.config.js': POSTCSS_CONFIG,
  'tailwind.config.js': TAILWIND_CONFIG,
  'index.html': INDEX_HTML,
  'src/index.css': INDEX_CSS,
  'src/main.tsx': MAIN_TSX,
  'src/lib/utils.ts': UTILS_TS,
  'src/components/app/AppShell.tsx': APP_SHELL_TSX,
  'src/components/ui/button.tsx': BUTTON_TSX,
  'src/components/ui/input.tsx': INPUT_TSX,
  'src/components/ui/card.tsx': CARD_TSX,
};

/**
 * 禁止 AI 写入的路径模式（除了预设文件外的额外保护）
 */
export const PROTECTED_PATHS = [
  /^package\.json$/,
  /^tsconfig.*\.json$/,
  /^vite\.config\.(ts|js)$/,
  /^postcss\.config\.(js|cjs)$/,
  /^tailwind\.config\.(js|ts)$/,
  /^src\/main\.(tsx|jsx)$/,          // 保护 main 入口文件（包含 Router）
  /^src\/index\.css$/,               // 保护全局样式
  /^src\/lib\/utils\.(ts|js)$/,     // 保护工具函数
  /^src\/components\/app\//,         // 保护 AppShell 等全局组件
  /^src\/components\/ui\//,          // 保护预设的 UI 组件（button, input, card 等）
  /^index\.html$/,
  /^src\/index\.css$/,
  /^src\/main\.tsx$/,
  /^src\/lib\/utils\.ts$/,
  /^src\/components\/app\//,
  /^src\/components\/ui\//,
];

