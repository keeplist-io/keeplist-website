/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
      extend: {
        colors: {
            "bkg-default": "hsl(var(--background-default) / <alpha-value>)",
            "bkg-inverted": "hsl(var(--background-inverted) / <alpha-value>)",
            "bkg-brand": "hsl(var(--background-brand) / <alpha-value>)",
            "bkg-surface": "hsl(var(--background-surface) / <alpha-value>)",
            "bkg-subtle": "hsl(var(--background-subtle) / <alpha-value>)",
            "bkg-neutral": "hsl(var(--background-neutral) / <alpha-value>)",
            "bkg-secondary": "hsl(var(--background-secondary) / <alpha-value>)",

            "content-primary": "hsl(var(--content-primary) / <alpha-value>)",
            "content-secondary": "hsl(var(--content-secondary) / <alpha-value>)",
            "content-tertiary": "hsl(var(--content-tertiary) / <alpha-value>)",
            "content-disabled": "hsl(var(--content-disabled) / <alpha-value>)",
            "content-inverted-primary": "hsl(var(--content-inverted-primary) / <alpha-value>)",
            "content-success": "hsl(var(--content-success) / <alpha-value>)",
            "content-error": "hsl(var(--content-error) / <alpha-value>)",
            "content-warning": "hsl(var(--content-warning) / <alpha-value>)",

            "border-normal": "hsl(var(--border-normal) / <alpha-value>)",
            "border-inverted": "hsl(var(--border-inverted) / <alpha-value>)",
            "border-secondary": "hsl(var(--border-secondary) / <alpha-value>)",
            "border-tertiary": "hsl(var(--border-tertiary) / <alpha-value>)",
            "border-selected": "hsl(var(--border-selected) / <alpha-value>)",

            "action-primary-normal": "hsl(var(--action-primary-normal) / <alpha-value>)",
            "action-secondary-normal": "hsl(var(--action-secondary-normal) / <alpha-value>)",
            "action-tertiary-selected": "hsl(var(--action-tertiary-selected) / <alpha-value>)",
            "action-inverted-pressed": "hsl(var(--action-inverted-pressed) / <alpha-value>)",
        },
      },
    },
    plugins: [],
  };