import * as React from "react"
import { cva } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-sm font-bold border-3 border-black ring-offset-background transition-all duration-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 shadow-brutal hover:shadow-none hover:translate-x-1 hover:translate-y-1 active:shadow-none active:translate-x-1 active:translate-y-1",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground border-black",
        destructive: "bg-destructive text-destructive-foreground border-black",
        outline: "border-3 border-black bg-white text-foreground hover:bg-secondary",
        secondary: "bg-secondary text-secondary-foreground border-black",
        ghost: "border-0 shadow-none hover:bg-secondary",
        link: "border-0 shadow-none text-primary underline-offset-4 hover:underline",
        hero: "bg-primary text-primary-foreground border-black font-black text-lg shadow-brutal-lg hover:shadow-none",
        heroOutline: "border-4 border-black bg-white text-foreground hover:bg-primary hover:text-primary-foreground font-black text-lg shadow-brutal-lg hover:shadow-none",
      },
      size: {
        default: "h-12 px-6 py-2 text-sm",
        sm: "h-10 px-4 text-sm",
        lg: "h-14 px-8 text-base",
        xl: "h-16 px-10 text-lg",
        icon: "h-12 w-12",
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
