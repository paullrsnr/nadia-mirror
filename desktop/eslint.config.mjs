import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";

export default tseslint.config(
  { ignores: ["dist/**", "node_modules/**"] },

  ...tseslint.configs.recommended,

  // Règles communes à tous les fichiers TS/TSX
  {
    plugins: { "react-hooks": reactHooks },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "@typescript-eslint/no-explicit-any": "error",
      // Pattern valide (reset d'état sur changement de dépendance) — warn only
      "react-hooks/set-state-in-effect": "warn",
    },
  },

  // Garantie CLAUDE.md : hooks .ts exportés doivent avoir un type de retour explicite
  {
    files: ["**/*.ts"],
    rules: {
      "@typescript-eslint/explicit-module-boundary-types": "error",
    },
  },
);
