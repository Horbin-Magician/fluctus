import AMapLoader from '@amap/amap-jsapi-loader'

let amapLoadPromise: Promise<unknown> | null = null

export function preloadAmap() {
  if (amapLoadPromise) return amapLoadPromise

  if (typeof window !== 'undefined') {
    window._AMapSecurityConfig = {
      securityJsCode: '467acecf4320cdce83d519705e1aad3b'
    }
  }

  amapLoadPromise = AMapLoader.load({
    key: '3fbe22db53162479e06074420635fba4',
    version: '2.0',
    plugins: ['AMap.Scale', 'AMap.PlaceSearch', 'AMap.AutoComplete']
  }).catch((error) => {
    amapLoadPromise = null
    throw error
  })

  return amapLoadPromise
}
