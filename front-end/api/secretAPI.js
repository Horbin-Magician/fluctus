/*
包含应用中所有与秘密树洞有关的api
 */
import ajax from './ajax'

export const getSecret = () => {
    return ajax('/api/secret', {'type':'get'}, 'POST')
}

export const updateSecret = (state=undefined, message=undefined) => {
    return ajax('/api/secret', {'type':'update', state, message}, 'POST')
}

export const updateState = (state) => {
    return updateSecret(state)
}

export const updateMessage = (message) => {
    return updateSecret(undefined, message)
}