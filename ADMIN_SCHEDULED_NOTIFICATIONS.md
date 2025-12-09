# Gerenciamento de Notificações Agendadas via Admin

Este documento explica como gerenciar as notificações push agendadas através da interface administrativa do Django.

## Acesso ao Admin

1. Acesse o admin do Django em `/admin/`
2. Faça login com credenciais administrativas

## Gerenciando Notificações Agendadas

### Visualizando Notificações

Na seção "Core" do admin, você encontrará "Scheduled notifications":

- **Título**: Título da notificação
- **Horário Agendado**: Hora do dia em que a notificação deve ser enviada
- **Ativo**: Se a notificação está ativa ou não
- **Último Envio**: Quando foi a última vez que esta notificação foi enviada
- **Próximo Envio**: Quando será o próximo envio (calculado automaticamente)

### Criando uma Nova Notificação

1. Clique em "ADICIONAR SCHEDULED NOTIFICATION"
2. Preencha os campos:
   - **Título**: Título da notificação (ex: "Lembrete de Transações")
   - **Corpo**: Mensagem da notificação
   - **Horário Agendado**: Hora do dia (formato HH:MM)
   - **Ativo**: Marque para ativar a notificação
   - **Ícone**: URL do ícone (opcional)
   - **URL**: URL para redirecionar ao clicar (opcional)

### Editando Notificações Existentes

1. Clique no título da notificação que deseja editar
2. Modifique os campos necessários
3. Salve as alterações

### Desativando Notificações

Para desativar uma notificação temporariamente:
1. Edite a notificação
2. Desmarque o campo "Ativo"
3. Salve

### Removendo Notificações

Para remover permanentemente uma notificação:
1. Marque a checkbox da notificação
2. Selecione "Delete selected scheduled notifications" no menu de ações
3. Confirme a exclusão

## Notificações Atuais

Atualmente existem duas notificações configuradas:

1. **Lembrete de Transações** (08:00)
   - Mensagem: "Bom dia! Não esqueça de registrar suas transações do dia."
   - Objetivo: Incentivar o registro diário de transações

2. **Gestão Financeira** (18:00)
   - Mensagem: "Boa noite! Lembre-se da importância da gestão financeira diária."
   - Objetivo: Reforçar a importância da gestão financeira

## Monitoramento

### Verificando Envios

- O campo "Último Envio" mostra quando foi a última vez que a notificação foi enviada
- O campo "Próximo Envio" calcula automaticamente quando será o próximo envio

### Logs de Notificações

Para ver os logs detalhados de envio:
1. Vá para "Push notification logs" no admin
2. Filtre por data e status para acompanhar o envio das notificações

## Configuração do Cron Job

Para que as notificações sejam enviadas automaticamente, configure um cron job no servidor:

```bash
# Executar a cada hora para verificar notificações pendentes
0 * * * * /caminho/para/venv/bin/python /caminho/para/projeto/manage.py send_scheduled_notifications
```

Ou para execução mais frequente (a cada 15 minutos):

```bash
*/15 * * * * /caminho/para/venv/bin/python /caminho/para/projeto/manage.py send_scheduled_notifications
```

## Dicas de Uso

- **Teste as notificações**: Use o botão "Testar Notificação" nas configurações do usuário antes de ativar
- **Horários apropriados**: Considere fusos horários dos usuários ao definir horários
- **Mensagens claras**: Mantenha as mensagens concisas e acionáveis
- **Frequência**: Não abuse das notificações para evitar desativação pelos usuários
- **Monitoramento**: Regularmente verifique os logs para garantir que as notificações estão sendo enviadas

## Solução de Problemas

### Notificações não estão sendo enviadas

1. Verifique se o cron job está configurado corretamente
2. Confirme se as notificações estão marcadas como "Ativo"
3. Verifique os logs de erro no admin
4. Certifique-se de que há usuários com subscrições push ativas

### Horários incorretos

- Verifique o fuso horário do servidor
- Confirme se o campo "Horário Agendado" está no formato correto (HH:MM)

### Usuários não recebem notificações

- Verifique se os usuários têm subscrições push ativas
- Confirme se as chaves VAPID estão configuradas corretamente
- Teste notificações manuais através da interface do usuário