module.exports = {
  goTemplateBracketSpacing: true,
  htmlWhitespaceSensitivity: "css",
  printWidth: 100,
  singleQuote: false,
  tabWidth: 2,
  trailingComma: "es5",

  overrides: [
    {
      files: ["*.html"],
      options: {
        parser: "go-template",
      },
    },
  ],
  plugins: [
    require.resolve("prettier-plugin-go-template"),
    require.resolve("prettier-plugin-tailwindcss"),
  ],
};
