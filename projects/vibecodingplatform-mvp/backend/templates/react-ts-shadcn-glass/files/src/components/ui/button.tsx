import * as React from "react"
import { cva } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-2xl font-medium ring-offset-background transition-all duration-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-white/20 backdrop-blur-lg border border-white/30 text-foreground hover:bg-white/30 shadow-sm",
        destructive: "bg-destructive/80 backdrop-blur-lg text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-primary/40 bg-transparent backdrop-blur-sm text-foreground hover:bg-primary/10",
        secondary: "bg-white/10 backdrop-blur-lg border border-white/20 text-foreground hover:bg-white/20",
        ghost: "hover:bg-white/10 backdrop-blur-sm",
        link: "text-primary underline-offset-4 hover:underline",
        hero: "bg-gradient-to-r from-primary to-accent text-primary-foreground font-semibold backdrop-blur-lg shadow-lg hover:shadow-xl hover:scale-102 transition-all duration-400",
        heroOutline: "border-2 border-primary/50 bg-white/10 backdrop-blur-lg text-foreground hover:bg-white/20 hover:border-primary font-semibold transition-all duration-400",
      },
      size: {
        default: "h-10 px-6 py-2 text-sm",
        sm: "h-9 rounded-xl px-4 text-sm",
        lg: "h-12 rounded-2xl px-8 text-base",
        xl: "h-14 rounded-2xl px-10 text-lg",
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
