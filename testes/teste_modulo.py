import pathlib
from playwright.sync_api import sync_playwright
import json
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(viewport={'width':1280,'height':900})
    pg.on('pageerror',lambda e:errs.append('pageerror: '+str(e)))
    pg.on('console',lambda m:errs.append('console.'+m.type+': '+m.text) if m.type in('error',) else None)
    pg.goto((pathlib.Path(__file__).resolve().parent.parent/'index.html').as_uri())
    pg.wait_for_timeout(500)
    out={}
    out['abas']=pg.eval_on_selector_all('[role=tab]','els=>els.map(e=>e.textContent.trim())')
    # preenche dados
    d="#tab-dados"
    def q(sel): return pg.locator(f'{d} {sel}')
    q('#nome').fill('Esporte para Todos')
    q('#tipo').select_option('Termo de fomento')
    q('#conc').select_option('Ministério do Esporte')
    q('#num').fill('912346'); q('#ano').fill('2026')
    q('#rep').fill('800000'); q('#cf').fill('100000'); q('#cb').fill('100000')
    out['global']=q('#mG').inner_text()
    out['cnpj']=q('#cnpj').input_value()
    q('#ini').fill('2026-03-01'); q('#fim').fill('2027-06-30')
    q('#obj').fill('Promover esporte para jovens')
    out['cabecalho']=[pg.inner_text('#hNome'),pg.inner_text('#hInst'),pg.inner_text('#hVig')]
    # botao +
    q('[data-new=tipo]').click()
    pg.wait_for_timeout(200)
    out['dialogo_tipo']=q('#dlgN').evaluate('d=>d.open')
    q('#nN').fill('Acordo de cooperação'); q('#dlgN button[type=submit]').click()
    out['tipo_novo_sel']=q('#tipo').input_value()
    # municipio
    q('[data-new=mun]').click(); q('#nN').fill('Recife'); q('#nUf').select_option('PE'); q('#dlgN button[type=submit]').click()
    out['mun_marcado']=q('#muns input:checked').evaluate_all('els=>els.map(e=>e.value)')
    # vai para metas
    pg.click('#t-metas'); pg.wait_for_timeout(200)
    m="#tab-metas"
    out['obj_na_aba_metas']=pg.locator(f'{m} #objRO').inner_text()
    out['benef_previstos']=pg.locator(f'{m} #mP').inner_text()
    out['benef_no_cadastro']=q('#benef').input_value()
    pg.click(f'{m} #bNew'); pg.wait_for_timeout(150)
    pg.fill(f'{m} #fDesc','Meta de teste'); pg.select_option(f'{m} #fUn','Turmas'); pg.fill(f'{m} #fPrev','10')
    pg.fill(f'{m} #fInd','x'); pg.locator(f'{m} #fCp input').first.check(force=True)
    pg.fill(f'{m} #fPrazo','2028-01-01'); pg.select_option(f'{m} #fResp','Ana Ribeiro')
    pg.click(f'{m} #mForm button[type=submit]')
    out['prazo_fora_vigencia']=pg.locator(f'{m} #fEr').inner_text()
    pg.fill(f'{m} #fPrazo','2027-01-01'); pg.click(f'{m} #mForm button[type=submit]')
    out['metas']=pg.locator(f'{m} #mN').inner_text()
    out['benef_apos']=pg.locator(f'{m} #mP').inner_text()
    # docs
    pg.click('#t-docs'); pg.wait_for_timeout(200)
    out['docs_m1']=pg.locator('#tab-docs #m1').inner_text()
    # perfil
    pg.select_option('#perfil','Financeiro'); pg.wait_for_timeout(200)
    out['financeiro_banner']=[pg.locator('#tab-docs #banner').evaluate('e=>e.classList.contains("show")'),
        pg.locator('#tab-metas #bNew').is_disabled()]
    out['selos']=pg.eval_on_selector_all('.bdg','els=>els.map(e=>e.textContent)')
    pg.select_option('#perfil','Projetos (máxima)'); pg.click('#t-dados'); pg.wait_for_timeout(200)
    pg.set_viewport_size({'width':390,'height':800}); pg.wait_for_timeout(200)
    out['overflow_horizontal_mobile']=pg.evaluate('document.documentElement.scrollWidth>innerWidth')
    b.close()
print(json.dumps(out,ensure_ascii=False,indent=1))
print('ERROS:',errs)
