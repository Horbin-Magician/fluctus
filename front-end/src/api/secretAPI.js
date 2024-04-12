/*
包含应用中所有与秘密树洞有关的api
 */
import ajax from './ajax'

export const getState = () => {
    return ajax('/api/secret/state', {'type':'get'}, 'POST')
}

export const updateState = (state) => {
    return ajax('/api/secret/state', {'type':'update', state}, 'POST')
}

export const getSecret = () => {
    return ajax('/api/secret/secretItem', {'type':'get'}, 'POST')
}

export const getMessage = () => {
    return ajax('/api/secret/message', {'type':'get'}, 'POST')
}

export const updateMessage = (message) => {
    return ajax('/api/secret/message', {'type':'set', message}, 'POST')
}