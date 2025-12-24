# quitspyingonme Visual Style Guide

## Brand Ethos
**We're done with surveillance capitalism bullshit.**

This isn't another tech company pretending to care while harvesting your data. We build tools that actually protect your privacy because we're sick of the internet being a dystopian nightmare.

### Core Values
- **Honest**: No dark patterns, no hidden fees, no corporate doublespeak
- **Human**: Built by people who actually use this shit, not MBAs
- **Direct**: Say what you mean, mean what you say
- **Protective**: Your privacy isn't a product to be sold

## Visual Identity

### Logo & Wordmark
- **Primary**: `quitspyingonme` (lowercase, one word)
- **Short form**: `qsm` when space is tight
- **Never**: QuitSpyingOnMe, Quit Spying On Me, or any corporate title case bullshit

### Color Palette

**Primary Colors**
- **Signal Green**: `#00D924` - The color of encrypted messages and actual privacy
- **Void Black**: `#0A0A0A` - Dark enough to hide from data brokers
- **Clean White**: `#FAFAFA` - Not pure white because that's harsh on eyes

**Secondary Colors**
- **Warning Orange**: `#FF6B35` - For when shit's about to go wrong
- **Error Red**: `#DC2626` - When something's actually broken
- **Info Blue**: `#3B82F6` - For helpful information that isn't trying to sell you anything
- **Success Green**: `#10B981` - When things work as they should

**Neutral Grays**
- **Text Dark**: `#1F1F1F`
- **Text Medium**: `#525252`
- **Text Light**: `#A3A3A3`
- **Border**: `#E5E5E5`
- **Background**: `#F5F5F5`

### Typography

**Primary Font: Inter**
- Clean, readable, doesn't try to be fancy
- Use system fonts as fallback: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`

**Font Weights**
- **Regular (400)**: Body text, most UI elements
- **Medium (500)**: Buttons, form labels
- **Semibold (600)**: Headings, important callouts
- **Bold (700)**: Only for emphasis, not decoration

**Font Sizes**
- **Heading 1**: 32px - Page titles
- **Heading 2**: 24px - Section headers
- **Heading 3**: 20px - Subsections
- **Body**: 16px - Default text
- **Small**: 14px - Secondary info, captions
- **Tiny**: 12px - Legal text, timestamps

## Design Principles

### DO
- **Use plenty of white space** - Let content breathe
- **Make buttons look like buttons** - No mystery meat navigation
- **Show system status clearly** - "Your email is forwarded" not "Processing..."
- **Use consistent spacing** - 8px grid system (8, 16, 24, 32, 48, 64px)
- **Write like a human** - "This alias forwards to your real email" not "This forwarding mechanism facilitates..."
- **Make errors helpful** - "Check your SMTP settings" not "Error 500"
- **Use icons sparingly** - Only when they actually help understanding

### DON'T
- **Use dark patterns** - No hidden checkboxes, no confusing cancellation flows
- **Animate everything** - Motion should have purpose, not just look cool
- **Use corporate stock photos** - Real screenshots or simple illustrations only
- **Hide important info** - Pricing, limitations, how things work should be obvious
- **Use jargon** - "Email alias" not "Electronic correspondence forwarding proxy"
- **Make users hunt for basic functions** - Delete account should be easy to find
- **Use popup modals for everything** - They're annoying as fuck

## UI Components

### Buttons
**Primary Button**
- Background: Signal Green `#00D924`
- Text: Void Black `#0A0A0A`
- Padding: 12px 24px
- Border radius: 6px
- Font weight: Medium (500)

**Secondary Button**
- Background: Clean White `#FAFAFA`
- Border: 1px solid Border `#E5E5E5`
- Text: Text Dark `#1F1F1F`
- Same padding and radius as primary

**Danger Button**
- Background: Error Red `#DC2626`
- Text: Clean White `#FAFAFA`
- Use for destructive actions like "Delete Account"

### Forms
- **Input fields**: 1px border, 8px padding, 6px radius
- **Labels**: Above inputs, not floating or inside
- **Required fields**: Mark with asterisk, not red text
- **Error states**: Red border + helpful error message below
- **Success states**: Green border + confirmation message

### Cards
- **Background**: Clean White `#FAFAFA`
- **Border**: 1px solid Border `#E5E5E5`
- **Border radius**: 8px
- **Padding**: 24px
- **Shadow**: Subtle, not dramatic

## Voice & Tone

### Writing Style
- **Conversational**: Write like you're explaining to a friend
- **Direct**: Get to the point quickly
- **Honest**: Admit limitations, don't oversell
- **Helpful**: Anticipate what users actually need to know

### Example Copy

**Good**:
- "Create an alias to hide your real email"
- "This forwards emails to your inbox"
- "We don't read your emails or sell your data"
- "Shit's broken. We're fixing it."

**Bad**:
- "Leverage our innovative email forwarding solution"
- "Experience seamless email management"
- "We're committed to your privacy journey"
- "We apologize for any inconvenience this may cause"

### Error Messages
- **Be specific**: "SMTP server rejected your password" not "Authentication failed"
- **Be helpful**: Include next steps or links to help
- **Be human**: "Something went wrong" is better than "An error occurred"

## Layout & Spacing

### Grid System
- **Container max-width**: 1200px
- **Breakpoints**: 
  - Mobile: 320px+
  - Tablet: 768px+
  - Desktop: 1024px+
- **Gutters**: 24px on mobile, 32px on desktop

### Spacing Scale
Use multiples of 8px for consistent spacing:
- **4px**: Tight spacing (icon to text)
- **8px**: Small gaps
- **16px**: Default spacing between elements
- **24px**: Section spacing
- **32px**: Large gaps
- **48px**: Major section breaks
- **64px**: Page-level spacing

## Accessibility

### Color Contrast
- All text meets WCAG AA standards (4.5:1 ratio minimum)
- Interactive elements have clear focus states
- Don't rely on color alone to convey information

### Interaction
- **Focus indicators**: Visible on all interactive elements
- **Touch targets**: Minimum 44px for mobile
- **Keyboard navigation**: Everything should be accessible via keyboard

## Brand Applications

### Website
- Clean, minimal layout
- Clear navigation
- No popup bullshit
- Fast loading (no tracking scripts slowing things down)

### Email Communications
- Plain text preferred
- HTML only when necessary
- No tracking pixels
- Unsubscribe link that actually works

### Documentation
- Clear headings and structure
- Code examples that actually work
- No marketing fluff in technical docs

## What We're Not

We're not trying to be:
- **Corporate**: No suits, no boardroom bullshit
- **Trendy**: Good design doesn't need to follow every fad
- **Cute**: Privacy tools should be serious, not playful
- **Everything to everyone**: We solve one problem well

## Implementation Notes

### CSS Custom Properties
```css
:root {
  --color-signal-green: #00D924;
  --color-void-black: #0A0A0A;
  --color-clean-white: #FAFAFA;
  --color-warning-orange: #FF6B35;
  --color-error-red: #DC2626;
  --color-info-blue: #3B82F6;
  --color-success-green: #10B981;
  
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --border-radius: 6px;
  --spacing-unit: 8px;
}
```

### Component Naming
Use clear, descriptive class names:
- `.button-primary` not `.btn-1`
- `.email-alias-card` not `.card-type-a`
- `.error-message` not `.msg-err`

---

**Remember**: This isn't about looking pretty. It's about building something that actually works for people who are tired of being the product.