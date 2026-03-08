import axios from 'axios'

console.log('Testing API connection...')
console.log('Base URL:', axios.defaults.baseURL)

try {
  const response = await axios.get('http://localhost:8888/api/v1/card-types')
  console.log('API Response:', response.data)
  console.log('Number of card types:', response.data.length)
} catch (error) {
  console.error('API Error:', error)
}
