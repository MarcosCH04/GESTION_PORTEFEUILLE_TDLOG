/** PostCSS is a CSS processor that transforms CSS with plugins
 * It is required by Tailwind CSS to process the styles correctly 
 * and add vendor prefixes for browser compatibility
 */
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
