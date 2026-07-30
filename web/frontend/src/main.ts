import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import './styles/base.css'
import './styles/resizable-layout.css'
document.documentElement.dataset.app = 'morphology-studio'
createApp(App).use(createPinia()).use(ElementPlus).mount('#app')
