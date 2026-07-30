/// <reference types="vite/client" />

declare module 'opencascade.js' {
  const initialize: () => Promise<unknown>
  export default initialize
}
