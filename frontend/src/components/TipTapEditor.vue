<template>
  <div class="overflow-hidden rounded-lg border border-default bg-default">
    <div
      v-if="editor && editable"
      class="flex flex-wrap items-center gap-0.5 border-b border-default bg-elevated/50 p-1.5"
    >
      <UButton
        size="xs"
        color="neutral"
        variant="ghost"
        square
        icon="i-lucide-bold"
        title="Жирный"
        :class="{ 'bg-muted': editor.isActive('bold') }"
        @click="editor.chain().focus().toggleBold().run()"
      />
      <UButton
        size="xs"
        color="neutral"
        variant="ghost"
        square
        icon="i-lucide-italic"
        title="Курсив"
        :class="{ 'bg-muted': editor.isActive('italic') }"
        @click="editor.chain().focus().toggleItalic().run()"
      />
      <UButton
        size="xs"
        color="neutral"
        variant="ghost"
        square
        icon="i-lucide-heading-2"
        title="Заголовок"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
      />
      <UButton
        size="xs"
        color="neutral"
        variant="ghost"
        square
        icon="i-lucide-list"
        title="Маркированный список"
        @click="editor.chain().focus().toggleBulletList().run()"
      />
      <UButton
        size="xs"
        color="neutral"
        variant="ghost"
        square
        icon="i-lucide-list-ordered"
        title="Нумерованный список"
        @click="editor.chain().focus().toggleOrderedList().run()"
      />
      <UButton
        size="xs"
        color="neutral"
        variant="ghost"
        square
        icon="i-lucide-code-2"
        title="Блок кода"
        @click="editor.chain().focus().toggleCodeBlock().run()"
      />
      <UButton
        size="xs"
        color="neutral"
        variant="ghost"
        square
        icon="i-lucide-link"
        title="Ссылка"
        @click="setLink"
      />
      <UButton
        size="xs"
        color="primary"
        variant="soft"
        square
        icon="i-lucide-image-plus"
        title="Изображение"
        @click="pickImage"
      />
      <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFile" />
    </div>
    <EditorContent :editor="editor" class="task-editor-content min-h-[240px] px-3 py-2" />
  </div>
</template>

<script setup lang="ts">
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import Placeholder from '@tiptap/extension-placeholder'
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import { onBeforeUnmount, ref, watch } from 'vue'

import { useApi } from '@/composables/useApi'

const props = defineProps<{
  modelValue: string | null
  editable?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
}>()

const { request } = useApi()
const fileInput = ref<HTMLInputElement | null>(null)

function parseContent(): Record<string, unknown> {
  if (!props.modelValue) return {}
  try {
    return JSON.parse(props.modelValue) as Record<string, unknown>
  } catch {
    return {}
  }
}

const editorInst = useEditor({
  extensions: [
    StarterKit.configure({ heading: { levels: [2, 3] } }),
    Placeholder.configure({
      placeholder: 'Текст задачи: списки, код, ссылки, картинки…',
    }),
    Link.configure({ openOnClick: true, autolink: true }),
    Image.configure({ inline: false, allowBase64: false }),
  ],
  content: parseContent(),
  editorProps: {
    handlePaste(_view, event) {
      const items = event.clipboardData?.items
      if (!items) return false
      for (const item of items) {
        if (item.type.startsWith('image/')) {
          event.preventDefault()
          const file = item.getAsFile()
          if (file) void uploadAndInsert(file)
          return true
        }
      }
      return false
    },
    handleDrop(_view, event) {
      const dt = event.dataTransfer
      if (!dt?.files?.length) return false
      const file = dt.files[0]
      if (file?.type.startsWith('image/')) {
        event.preventDefault()
        void uploadAndInsert(file)
        return true
      }
      return false
    },
  },
  onUpdate: ({ editor }) => {
    emit('update:modelValue', JSON.stringify(editor.getJSON()))
  },
  editable: props.editable ?? true,
})

async function uploadAndInsert(file: File) {
  const body = new FormData()
  body.append('file', file)
  const { url } = await request<{ url: string }>('/api/upload', { method: 'POST', body })
  const ed = editorInst.value
  if (!ed) return
  ed.chain().focus().setImage({ src: url }).run()
}

const editor = editorInst

watch(
  () => props.modelValue,
  (next) => {
    const ed = editorInst.value
    if (!ed) return
    const cur = JSON.stringify(ed.getJSON())
    const incoming = next ? JSON.stringify(JSON.parse(next)) : '{}'
    if (cur !== incoming) {
      ed.commands.setContent(parseContent(), { emitUpdate: false })
    }
  },
)

watch(
  () => props.editable,
  (next) => {
    editorInst.value?.setEditable(next ?? true)
  },
)

function setLink() {
  const ed = editorInst.value
  if (!ed) return
  const prev = ed.getAttributes('link').href as string | undefined
  const url = window.prompt('URL ссылки', prev ?? 'https://')
  if (url === null) return
  if (url === '') {
    ed.chain().focus().extendMarkRange('link').unsetLink().run()
    return
  }
  ed.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
}

function pickImage() {
  fileInput.value?.click()
}

function onFile(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (file) void uploadAndInsert(file)
}

onBeforeUnmount(() => {
  editorInst.value?.destroy()
})
</script>

<style scoped>
.task-editor-content :deep(.ProseMirror) {
  outline: none;
  min-height: 200px;
}
.task-editor-content :deep(.ProseMirror p.is-editor-empty:first-child::before) {
  color: var(--ui-text-muted);
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}
.task-editor-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.375rem;
}
.task-editor-content :deep(pre) {
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  background: var(--ui-bg-elevated);
  overflow-x: auto;
}
</style>
