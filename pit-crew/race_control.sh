#!/usr/bin/env bash
# Race control · instructor helper for the AI-901 Grand Prix (run in Azure Cloud Shell as a subscription Owner)
#   ./race_control.sh prep                 register providers, check quotas in eastus2
#   ./race_control.sh roles students.txt   grant Contributor + Foundry User (formerly Azure AI User) + Cognitive Services User at subscription scope to each UPN in the file (one per line)
#   ./race_control.sh status               list every rg-ai901-* group, its resources and deployments
#   ./race_control.sh cost                 cost by student resource group for today (data lags a few hours)
#   ./race_control.sh cleanup              delete every rg-ai901-* group and purge soft-deleted Foundry resources
set -euo pipefail
LOC=${LOC:-eastus2}; SUB=$(az account show --query id -o tsv)
case "${1:-}" in
  prep)
    for ns in Microsoft.CognitiveServices Microsoft.Storage Microsoft.KeyVault Microsoft.Insights; do az provider register --namespace $ns -o none; done
    echo "Quotas in $LOC (need: gpt4.1-mini Standard ≥ 8K × students, gpt4.1 GlobalStandard ≥ 40K × students, gpt-audio-mini GlobalStandard ≥ 1 × students, FLUX.2-pro ≥ 1 × students, text-embedding-3-large Standard ≥ 10K × students, AIServices accounts ≥ students):"
    az cognitiveservices usage list --location $LOC --query "[?limit > \`0\` && (contains(name.value,'Standard.gpt4.1-mini') || name.value=='OpenAI.GlobalStandard.gpt4.1' || contains(name.value,'gpt-audio-mini') || contains(name.value,'FLUX.2-pro') || contains(name.value,'text-embedding-3-large') || contains(name.value,'AIServices.S0'))].{quota:name.value,used:currentValue,limit:limit}" -o table ;;
  roles)
    while read -r upn; do [ -z "$upn" ] && continue
      for role in b24988ac-6180-42a0-ab88-20f7382dd24c 53ca6127-db72-4b80-b1b0-d745d6d5456d a97b65f3-24c7-4388-baec-2e87135dc908; do az role assignment create --assignee "$upn" --role "$role" --scope /subscriptions/$SUB -o none && echo "$upn ← $(az role definition list --name $role --query [0].roleName -o tsv)"; done  # Contributor, Foundry User, Cognitive Services User (IDs survive renames)
    done < "${2:?students.txt}" ;;
  status)
    for rg in $(az group list --query "[?starts_with(name,'rg-ai901')].name" -o tsv); do echo "== $rg"; az resource list -g $rg --query "[].{name:name,type:type}" -o table
      for acc in $(az cognitiveservices account list -g $rg --query "[].name" -o tsv); do az cognitiveservices account deployment list -g $rg -n $acc --query "[].{deployment:name,model:properties.model.name,sku:sku.name,capacity:sku.capacity}" -o table; done; done ;;
  cost)
    az consumption usage list --start-date $(date -u +%Y-%m-%d) --end-date $(date -u -d tomorrow +%Y-%m-%d 2>/dev/null || date -u -v+1d +%Y-%m-%d) --query "[?contains(instanceId,'rg-ai901')].{rg:instanceId,cost:pretaxCost,meter:meterName}" -o table 2>/dev/null || echo "cost data not available yet (it lags 4–24 hours)" ;;
  cleanup)
    for rg in $(az group list --query "[?starts_with(name,'rg-ai901')].name" -o tsv); do echo "deleting $rg"; az group delete -n $rg --yes --no-wait; done
    sleep 60
    az cognitiveservices account list-deleted --query "[?starts_with(name,'ai901')].{name:name,location:location,id:id}" -o tsv | while read -r name loc id; do rg=$(echo "$id" | sed -E 's#.*/resourceGroups/([^/]+)/.*#\1#'); echo "purging $name ($rg, $loc)"; az cognitiveservices account purge -n "$name" -g "$rg" -l "$loc" -o none || true; done ;;
  *) sed -n '2,8p' "$0" ;;
esac
