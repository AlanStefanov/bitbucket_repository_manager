# FAQ — Bitbucket Manager (ES)

## ¿Cómo creo un token de API de Bitbucket?
Andá a https://id.atlassian.com/manage-profile/security/api-tokens y creá un token. Scopes necesarios: `repository:read`, `repository:admin`, `pullrequest:read`, `pullrequest:write`, `workspace:membership:read`.

## ¿Dónde se guarda la configuración?
En `~/.config/bitbucket-manager/env`. Si no existe, la app muestra una pantalla interactiva de configuración.

## ¿Puedo usar archivos `.env`?
Sí. La app también lee `.env` en la raíz del proyecto y `~/.bbm/.env` (legacy).

## ¿Por qué `bitbucket-manager` y no `bbm` o `brm`?
`brm` ya estaba ocupado en PyPI (Bicycle Repair Man, 2022). `bbm` también (Buzzni Batch Monitor, 2024). `bitbucket-manager` estaba disponible y describe mejor el alcance.

## ¿Funciona en Windows?
La app está optimizada para Linux y macOS. Windows puede funcionar con WSL2 pero no es soportado oficialmente.

## ¿Cómo clono un repositorio?
Abrí la pantalla Repos desde el menú principal, seleccioná un repo y presioná Enter.

## ¿Cómo elimino un miembro de un grupo?
Andá a Grupos → seleccioná el grupo → ingresá el nickname del miembro y hacé clic en "Remover".

## Encontré un bug, ¿dónde lo reporto?
https://github.com/AlanStefanov/bitbucket-manager/issues
