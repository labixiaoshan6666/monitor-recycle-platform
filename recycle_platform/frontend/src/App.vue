<script setup>
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { api } from './api'

const types = ref([])
const brands = ref([])
const models = ref([])
const selectedType = ref('')
const selectedBrand = ref('')
const selectedModel = ref('')

const productInfo = ref(null)
const trendData = ref([])
const chartRef = ref(null)
let chartInstance

const policies = ref([])
const activePolicy = ref(null)
const loadingChart = ref(false)
const errorMessage = ref('')

// 搜索相关
const productSearchKeyword = ref('')
const policySearchKeyword = ref('')
const searchedProducts = ref([])
const searchingProducts = ref(false)
const searchingPolicies = ref(false)

const aiQuestion = ref('')
const aiMessages = ref([])
const aiLoading = ref(false)
const aiError = ref('')
const chatContainer = ref(null)

// 自动滚动到底部
const scrollToBottom = () => {
  if (chatContainer.value) {
    setTimeout(() => {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }, 100)
  }
}

const loadTypes = async () => {
  try {
    const { data } = await api.get('/types/')
    types.value = data
    if (!selectedType.value && data.length) {
      selectedType.value = data[0]
    }
  } catch (err) {
    console.error('加载类型失败:', err)
  }
}

const loadBrands = async () => {
  if (!selectedType.value) {
    brands.value = []
    return
  }
  try {
    const { data } = await api.get('/brands/', { params: { category: selectedType.value } })
    brands.value = data
    selectedBrand.value = data[0] || ''
  } catch (err) {
    console.error('加载品牌失败:', err)
    brands.value = []
  }
}

const loadModels = async () => {
  if (!selectedType.value || !selectedBrand.value) {
    models.value = []
    return
  }
  try {
    const { data } = await api.get('/models/', {
      params: { category: selectedType.value, brand: selectedBrand.value }
    })
    models.value = data
    selectedModel.value = data[0] || ''
  } catch (err) {
    console.error('加载型号失败:', err)
    models.value = []
  }
}

const loadTrend = async () => {
  if (!selectedType.value || !selectedBrand.value || !selectedModel.value) {
    trendData.value = []
    productInfo.value = null
    return
  }
  loadingChart.value = true
  try {
    const { data } = await api.get('/price-trend/', {
      params: {
        category: selectedType.value,
        brand: selectedBrand.value,
        model: selectedModel.value
      }
    })
    console.log('[DEBUG] API Response:', data)
    console.log('[DEBUG] History data:', data.history)
    console.log('[DEBUG] History length:', data.history?.length)
    
    productInfo.value = data.product
    trendData.value = data.history
    
    console.log('[DEBUG] trendData.value:', trendData.value)
    
    // 使用 nextTick 确保 DOM 更新后再渲染图表
    await nextTick()
    renderChart()
    errorMessage.value = ''
  } catch (err) {
    console.error('加载价格趋势失败:', err)
    errorMessage.value = '无法加载价格数据'
    trendData.value = []
  } finally {
    loadingChart.value = false
  }
}

const loadPolicies = async (keyword = '') => {
  searchingPolicies.value = true
  try {
    const params = keyword ? { keyword } : {}
    const { data } = await api.get('/policies/', { params })
    policies.value = data
    if (data.length && !activePolicy.value) {
      activePolicy.value = data[0]
    }
  } catch (err) {
    console.error('加载政策失败:', err)
  } finally {
    searchingPolicies.value = false
  }
}

// 搜索回收产品
const searchProducts = async () => {
  if (!productSearchKeyword.value.trim()) {
    searchedProducts.value = []
    return
  }
  searchingProducts.value = true
  try {
    const { data } = await api.get('/products/', { 
      params: { keyword: productSearchKeyword.value.trim() } 
    })
    searchedProducts.value = data
  } catch (err) {
    console.error('搜索产品失败:', err)
    searchedProducts.value = []
  } finally {
    searchingProducts.value = false
  }
}

// 搜索政策
const searchPolicies = async () => {
  await loadPolicies(policySearchKeyword.value.trim())
  if (policies.value.length > 0) {
    activePolicy.value = policies.value[0]
  } else {
    activePolicy.value = null
  }
}

// 清空产品搜索
const clearProductSearch = () => {
  productSearchKeyword.value = ''
  searchedProducts.value = []
}

// 清空政策搜索
const clearPolicySearch = () => {
  policySearchKeyword.value = ''
  loadPolicies()
}

// 选择搜索结果中的产品
const selectSearchedProduct = (product) => {
  selectedType.value = product.category
  selectedBrand.value = product.brand
  selectedModel.value = product.model
  clearProductSearch()
}

// AI问答功能
const sendAiQuestion = async () => {
  const question = aiQuestion.value.trim()
  if (!question) {
    aiError.value = '请输入问题'
    return
  }
  
  // 添加用户消息
  aiMessages.value.push({
    role: 'user',
    content: question,
    timestamp: new Date().toLocaleTimeString()
  })
  
  aiQuestion.value = ''
  aiLoading.value = true
  aiError.value = ''
  scrollToBottom()
  
  try {
    const { data } = await api.post('/ai-chat/', { 
      question,
      history: aiMessages.value.slice(-10) // 只发送最近10条历史记录
    })
    
    // 添加AI回复
    aiMessages.value.push({
      role: 'assistant',
      content: data.answer,
      timestamp: new Date().toLocaleTimeString()
    })
    scrollToBottom()
  } catch (err) {
    console.error('AI问答失败:', err)
    aiError.value = err.response?.data?.detail || '获取AI回复失败，请稍后重试'
    // 移除用户消息
    aiMessages.value.pop()
  } finally {
    aiLoading.value = false
  }
}

// 清空对话历史
const clearAiChat = () => {
  aiMessages.value = []
  aiError.value = ''
  aiQuestion.value = ''
}

const renderChart = () => {
  if (!chartRef.value) {
    console.error('[DEBUG] chartRef is null, cannot render')
    return
  }
  
  if (!chartInstance) {
    console.log('[DEBUG] Initializing new chart instance')
    chartInstance = echarts.init(chartRef.value)
  }
  
  console.log('[DEBUG] renderChart - trendData:', trendData.value)
  
  if (!trendData.value || trendData.value.length === 0) {
    console.warn('[DEBUG] No trend data to render')
    return
  }
  
  const dates = trendData.value.map(item => item.date)
  const prices = trendData.value.map(item => item.price)
  
  console.log('[DEBUG] Dates for chart:', dates)
  console.log('[DEBUG] Prices for chart:', prices)

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      borderColor: 'transparent',
      textStyle: {
        color: '#fff'
      },
      formatter: function(params) {
        if (params && params.length > 0) {
          const item = params[0]
          return `${item.name}<br/>价格: ¥${item.value}`
        }
        return ''
      }
    },
    grid: { left: 60, right: 30, top: 30, bottom: 50 },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false, // 始终设置为false，让折线从坐标轴开始
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { 
        fontSize: 12, 
        color: '#6b7280',
        rotate: dates.length > 5 ? 30 : 0
      }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      splitLine: { lineStyle: { color: '#f3f4f6' } },
      axisLabel: { 
        fontSize: 12, 
        color: '#6b7280',
        formatter: '¥{value}'
      },
      scale: true, // 自动调整范围
      minInterval: 1 // 最小间隔
    },
    series: [
      {
        data: prices,
        type: 'line',
        smooth: false, // 改为false，避免单点或双点时的渲染问题
        showSymbol: true,
        symbolSize: 8, // 统一大小，确保可见
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(37, 99, 235, 0.2)' },
            { offset: 1, color: 'rgba(37, 99, 235, 0.02)' }
          ])
        },
        lineStyle: { 
          width: 2, 
          color: '#2563eb'
        },
        itemStyle: {
          borderColor: '#2563eb',
          borderWidth: 2,
          color: '#fff'
        },
        label: {
          show: true, // 始终显示标签
          position: 'top',
          formatter: '¥{c}',
          color: '#2563eb',
          fontSize: 11,
          fontWeight: 600
        }
      }
    ]
  }

  console.log('[DEBUG] Setting chart option:', option)
  
  try {
    chartInstance.clear() // 清除旧图表
    chartInstance.setOption(option, true)
    chartInstance.resize() // 强制调整大小
    console.log('[DEBUG] Chart rendered successfully')
  } catch (error) {
    console.error('[DEBUG] Error rendering chart:', error)
  }
}

const handleResize = () => {
  chartInstance?.resize()
}

watch(selectedType, async () => {
  await loadBrands()
  await loadModels()
  await loadTrend()
})

watch(selectedBrand, async () => {
  await loadModels()
  await loadTrend()
})

watch(selectedModel, async () => {
  await loadTrend()
})

onMounted(async () => {
  await loadTypes()
  await loadBrands()
  await loadModels()
  await loadTrend()
  await loadPolicies()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<template>
  <div class="app">
    <header class="hero">
      <div>
        <h1>易可收</h1>
        <p>实时掌握二手家电回收行情，支持多品类、多品牌、多型号价格趋势跟踪。</p>
      </div>
      <div class="hero-card">
        <div class="label">今日监控产品</div>
        <div class="value">{{ productInfo ? productInfo.brand + ' ' + productInfo.model : '请选择产品' }}</div>
        <div class="sub">更新时间：{{ productInfo ? productInfo.scrape_date : '--' }}</div>
      </div>
    </header>

    <section class="panel">
      <h2>价格监控</h2>
      
      <!-- 产品搜索 -->
      <div class="search-box">
        <div class="search-input-wrapper">
          <input 
            v-model="productSearchKeyword" 
            type="text" 
            placeholder="搜索回收产品：输入品牌、型号、类型等关键词..."
            @keyup.enter="searchProducts"
            class="search-input"
          />
          <button @click="searchProducts" class="search-btn" :disabled="searchingProducts">
            {{ searchingProducts ? '搜索中...' : '🔍 搜索' }}
          </button>
          <button v-if="productSearchKeyword" @click="clearProductSearch" class="clear-btn">✕</button>
        </div>
        
        <!-- 搜索结果 -->
        <div v-if="searchedProducts.length > 0" class="search-results">
          <div class="search-results-header">
            找到 {{ searchedProducts.length }} 个相关产品
          </div>
          <div class="search-results-list">
            <div 
              v-for="product in searchedProducts" 
              :key="product.id"
              class="search-result-item"
              @click="selectSearchedProduct(product)"
            >
              <div class="product-info">
                <div class="product-name">{{ product.brand }} {{ product.model }}</div>
                <div class="product-meta">
                  <span class="tag">{{ product.category }}</span>
                  <span class="price">¥{{ product.avg_price }}</span>
                </div>
              </div>
              <div class="select-arrow">→</div>
            </div>
          </div>
        </div>
        <div v-else-if="productSearchKeyword && !searchingProducts && searchedProducts.length === 0" class="search-empty">
          未找到匹配的产品，请尝试其他关键词
        </div>
      </div>

      <div class="filters">
        <div class="filter-item">
          <label>家电类型</label>
          <select v-model="selectedType">
            <option v-for="item in types" :key="item" :value="item">{{ item }}</option>
          </select>
        </div>
        <div class="filter-item">
          <label>家电品牌</label>
          <select v-model="selectedBrand">
            <option v-for="item in brands" :key="item" :value="item">{{ item }}</option>
          </select>
        </div>
        <div class="filter-item">
          <label>家电型号</label>
          <select v-model="selectedModel">
            <option v-for="item in models" :key="item" :value="item">{{ item }}</option>
          </select>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <div>
            <div class="title">回收价格趋势（近7天）</div>
            <div class="subtitle">均价：{{ productInfo ? '¥' + productInfo.avg_price : '--' }}</div>
          </div>
          <div class="badge">实时更新</div>
        </div>
        <div v-if="errorMessage" style="color: #ef4444; padding: 12px; margin-bottom: 12px;">{{ errorMessage }}</div>
        <div v-if="loadingChart" style="padding: 60px 20px; text-align: center; color: #6b7280;">加载中...</div>
        <div v-show="!loadingChart" ref="chartRef" class="chart"></div>
      </div>
    </section>

    <section class="panel">
      <h2>以旧换新最新政策</h2>
      
      <!-- 政策搜索 -->
      <div class="search-box policy-search">
        <div class="search-input-wrapper">
          <input 
            v-model="policySearchKeyword" 
            type="text" 
            placeholder="搜索政策：输入政策标题、内容关键词..."
            @keyup.enter="searchPolicies"
            class="search-input"
          />
          <button @click="searchPolicies" class="search-btn" :disabled="searchingPolicies">
            {{ searchingPolicies ? '搜索中...' : '🔍 搜索' }}
          </button>
          <button v-if="policySearchKeyword" @click="clearPolicySearch" class="clear-btn">✕</button>
        </div>
        <div v-if="policySearchKeyword && policies.length === 0 && !searchingPolicies" class="search-empty">
          未找到匹配的政策，请尝试其他关键词
        </div>
      </div>

      <div class="policy-layout">
        <aside class="policy-list">
          <div
            v-for="policy in policies"
            :key="policy.id"
            :class="['policy-item', { active: activePolicy && policy.id === activePolicy.id }]"
            @click="activePolicy = policy"
          >
            <div class="policy-title">{{ policy.title }}</div>
            <div class="policy-date">{{ policy.publish_date }}</div>
          </div>
        </aside>
        <article class="policy-reader">
          <template v-if="activePolicy">
            <h3>{{ activePolicy.title }}</h3>
            <div class="policy-meta">发布日期：{{ activePolicy.publish_date }}</div>
            <div v-if="activePolicy.attachment_url" class="policy-file">
              <a :href="activePolicy.attachment_url" target="_blank" rel="noreferrer">📥 下载政策附件</a>
            </div>
            <div v-if="activePolicy.attachment_url && activePolicy.attachment_url.endsWith('.pdf')" class="pdf-preview">
              <iframe :src="activePolicy.attachment_url" title="政策附件"></iframe>
            </div>
            <div v-if="activePolicy.content" class="policy-content">{{ activePolicy.content }}</div>
            <div v-else-if="!activePolicy.attachment_url" class="empty">暂无文字内容，请查看附件。</div>
          </template>
          <div v-else class="empty">暂无政策信息</div>
        </article>
      </div>
    </section>

    <!-- AI问答区域 -->
    <section class="panel ai-panel">
      <div class="ai-header">
        <div>
          <h2>AI智能问答</h2>
          <p class="ai-subtitle">专业解答以旧换新政策相关问题</p>
        </div>
        <button v-if="aiMessages.length > 0" @click="clearAiChat" class="clear-chat-btn">清空对话</button>
      </div>
      
      <!-- 对话历史 -->
      <div class="ai-chat-container" ref="chatContainer">
        <div v-if="aiMessages.length === 0" class="ai-welcome">
          <div class="welcome-icon">🤖</div>
          <h3>欢迎使用AI政策助手</h3>
          <p>您可以向我咨询任何关于以旧换新政策的问题</p>
          <div class="example-questions">
            <div class="example-label">示例问题：</div>
            <button 
              v-for="(example, idx) in ['什么是以旧换新政策？', '如何参与以旧换新活动？', '以旧换新有哪些补贴？']" 
              :key="idx"
              @click="aiQuestion = example; sendAiQuestion()"
              class="example-btn"
            >
              {{ example }}
            </button>
          </div>
        </div>
        
        <div v-else class="ai-messages">
          <div 
            v-for="(message, idx) in aiMessages" 
            :key="idx"
            :class="['ai-message', message.role === 'user' ? 'user-message' : 'assistant-message']"
          >
            <div class="message-avatar">
              {{ message.role === 'user' ? '👤' : '🤖' }}
            </div>
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-time">{{ message.timestamp }}</div>
            </div>
          </div>
        </div>
        
        <!-- 加载中动画 -->
        <div v-if="aiLoading" class="ai-message assistant-message">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="aiError" class="ai-error">
        {{ aiError }}
      </div>
      
      <!-- 输入框 -->
      <div class="ai-input-wrapper">
        <textarea 
          v-model="aiQuestion" 
          placeholder="请输入您关于以旧换新政策的问题..."
          @keydown.enter.prevent="!aiLoading && sendAiQuestion()"
          class="ai-input"
          rows="3"
        ></textarea>
        <button 
          @click="sendAiQuestion" 
          :disabled="aiLoading || !aiQuestion.trim()"
          class="ai-send-btn"
        >
          <span v-if="aiLoading">发送中...</span>
          <span v-else>🚀 发送</span>
        </button>
      </div>
      
      <div class="ai-notice">
        <span class="notice-icon">ℹ️</span>
        AI回答仅供参考，具体政策以官方文件为准。
      </div>
    </section>
  </div>
</template>
