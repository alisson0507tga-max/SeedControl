from pathlib import Path
import re
import sys

MODE = sys.argv[1] if len(sys.argv) > 1 else '--web'
ROOT = Path('native/www')

WEB_JS = r'''// seedcontrol-ime-nativo-real-v3827
(function () {
    "use strict";

    let campoAtivo = null;
    let pluginLigado = false;
    let ativando = false;

    function plugin() {
        try {
            return window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.NativeIme;
        } catch (_) {
            return null;
        }
    }

    function paginaAtual() {
        return String(location.pathname || "").split("/").pop().toLowerCase();
    }

    function ehCampoTexto(el) {
        if (!el || el.disabled || el.readOnly) return false;
        if (el.tagName === "TEXTAREA") return true;
        if (el.tagName !== "INPUT") return false;
        return ["text", "search", "email", "url", "tel"].includes(String(el.type || "text").toLowerCase());
    }

    function camposVisiveisCadastro() {
        if (paginaAtual() !== "cadastro.html") return [];
        return Array.from(document.querySelectorAll("input, select, textarea"))
            .filter(function (el) {
                if (!el || el.disabled || el.readOnly || el.hidden || el.offsetParent === null) return false;
                if (el.tagName === "INPUT") {
                    const t = String(el.type || "text").toLowerCase();
                    if (["hidden", "file", "checkbox", "radio", "button", "submit", "reset", "image"].includes(t)) return false;
                }
                return true;
            });
    }

    function acaoDoCampo(campo) {
        if (paginaAtual() === "assistente-chat-v384.html") return "send";
        if (paginaAtual() === "cadastro.html") {
            const campos = camposVisiveisCadastro();
            const i = campos.indexOf(campo);
            return i >= 0 && i < campos.length - 1 ? "next" : "done";
        }
        return "done";
    }

    function marcar(campo, ativo) {
        if (!campo) return;
        campo.classList.toggle("seed-ime-nativo-ativo-v3827", !!ativo);
    }

    async function ativar(campo) {
        const p = plugin();
        if (!p || typeof p.focusInput !== "function" || !ehCampoTexto(campo) || ativando) return;

        ativando = true;
        try {
            if (campoAtivo && campoAtivo !== campo) marcar(campoAtivo, false);
            campoAtivo = campo;

            let inicio = String(campo.value || "").length;
            let fim = inicio;
            try {
                if (typeof campo.selectionStart === "number") inicio = campo.selectionStart;
                if (typeof campo.selectionEnd === "number") fim = campo.selectionEnd;
            } catch (_) {}

            // O foco real passa para um EditText Android. O HTML continua sendo
            // a interface visível e recebe o texto espelhado pelos eventos nativos.
            try { campo.blur(); } catch (_) {}
            marcar(campo, true);

            await p.focusInput({
                value: String(campo.value || ""),
                selectionStart: inicio,
                selectionEnd: fim,
                action: acaoDoCampo(campo)
            });
        } catch (erro) {
            marcar(campo, false);
            campoAtivo = null;
            try { campo.focus(); } catch (_) {}
            console.warn("SeedControl: entrada nativa indisponível; usando WebView.", erro);
        } finally {
            ativando = false;
        }
    }

    function aplicarTexto(valor, inicio, fim) {
        if (!campoAtivo) return;
        campoAtivo.value = String(valor == null ? "" : valor);
        campoAtivo.dispatchEvent(new Event("input", { bubbles: true }));
        try {
            campoAtivo.setSelectionRange(Number(inicio) || campoAtivo.value.length, Number(fim) || Number(inicio) || campoAtivo.value.length);
        } catch (_) {}
    }

    async function esconderNativo() {
        const p = plugin();
        if (p && typeof p.hideInput === "function") {
            try { await p.hideInput(); } catch (_) {}
        }
        if (campoAtivo) marcar(campoAtivo, false);
        campoAtivo = null;
    }

    async function proximoCampo() {
        if (!campoAtivo || paginaAtual() !== "cadastro.html") return;
        const atual = campoAtivo;
        const campos = camposVisiveisCadastro();
        const i = campos.indexOf(atual);
        const proximo = i >= 0 ? campos[i + 1] : null;

        if (!proximo) {
            await esconderNativo();
            return;
        }

        marcar(atual, false);
        campoAtivo = null;

        if (ehCampoTexto(proximo)) {
            await ativar(proximo);
        } else {
            await esconderNativo();
            try { proximo.focus({ preventScroll: true }); } catch (_) { try { proximo.focus(); } catch (_) {} }
            try { proximo.scrollIntoView({ behavior: "smooth", block: "center" }); } catch (_) {}
        }
    }

    function ligarPlugin() {
        if (pluginLigado) return;
        const p = plugin();
        if (!p || typeof p.addListener !== "function") return;
        pluginLigado = true;

        p.addListener("textChanged", function (d) {
            aplicarTexto(d && d.value, d && d.selectionStart, d && d.selectionEnd);
        });

        p.addListener("editorAction", async function (d) {
            const acao = String(d && d.action || "");
            if (acao === "send" && paginaAtual() === "assistente-chat-v384.html") {
                const botao = document.getElementById("enviar");
                await esconderNativo();
                if (botao) botao.click();
                return;
            }
            if (acao === "next" && paginaAtual() === "cadastro.html") {
                await proximoCampo();
                return;
            }
            if (acao === "done") await esconderNativo();
        });
    }

    function iniciar() {
        ligarPlugin();

        // O campo WebView recebe foco por um instante apenas para calcular a
        // posição do cursor. Em seguida o foco é transferido ao EditText nativo.
        document.addEventListener("focusin", function (e) {
            if (!ehCampoTexto(e.target)) return;
            setTimeout(function () { ativar(e.target); }, 0);
        }, true);

        document.addEventListener("click", function (e) {
            const alvo = e.target && e.target.closest ? e.target.closest("button") : null;
            if (!alvo) return;
            if (alvo.id === "enviar" || alvo.id === "microfone" || alvo.id === "salvar") {
                esconderNativo();
            }
        }, true);

        document.addEventListener("visibilitychange", function () {
            if (document.hidden) esconderNativo();
        });
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar, { once: true });
    else iniciar();
})();
'''

WEB_CSS = r'''/* seedcontrol-ime-nativo-real-v3827 */
.seed-ime-nativo-ativo-v3827 {
    border-color: rgba(74, 222, 128, .78) !important;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, .12) !important;
}
'''

JAVA_PLUGIN = r'''package br.com.seedcontrol.app;

import android.content.Context;
import android.graphics.Color;
import android.text.Editable;
import android.text.InputType;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputMethodManager;
import android.widget.EditText;
import android.widget.FrameLayout;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "NativeIme")
public class NativeImePlugin extends Plugin {
    private EditText nativeInput;
    private boolean internalChange = false;
    private String currentAction = "done";

    private void ensureInput() {
        if (nativeInput != null) return;

        nativeInput = new EditText(getActivity());
        nativeInput.setSingleLine(true);
        nativeInput.setBackgroundColor(Color.TRANSPARENT);
        nativeInput.setTextColor(Color.TRANSPARENT);
        nativeInput.setHintTextColor(Color.TRANSPARENT);
        nativeInput.setCursorVisible(false);
        nativeInput.setPadding(0, 0, 0, 0);
        nativeInput.setAlpha(0.01f);
        nativeInput.setInputType(
            InputType.TYPE_CLASS_TEXT |
            InputType.TYPE_TEXT_VARIATION_NORMAL |
            InputType.TYPE_TEXT_FLAG_AUTO_CORRECT |
            InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
        );

        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(2, 2);
        lp.gravity = Gravity.TOP | Gravity.START;
        lp.leftMargin = 1;
        lp.topMargin = 1;

        ViewGroup root = (ViewGroup) getActivity().findViewById(android.R.id.content);
        root.addView(nativeInput, lp);

        nativeInput.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {}

            @Override
            public void afterTextChanged(Editable s) {
                if (internalChange) return;
                JSObject data = new JSObject();
                data.put("value", s.toString());
                data.put("selectionStart", nativeInput.getSelectionStart());
                data.put("selectionEnd", nativeInput.getSelectionEnd());
                notifyListeners("textChanged", data);
            }
        });

        nativeInput.setOnEditorActionListener((v, actionId, event) -> {
            boolean reconhecida = actionId == EditorInfo.IME_ACTION_NEXT ||
                                  actionId == EditorInfo.IME_ACTION_SEND ||
                                  actionId == EditorInfo.IME_ACTION_DONE ||
                                  actionId == EditorInfo.IME_ACTION_GO ||
                                  actionId == EditorInfo.IME_ACTION_UNSPECIFIED;
            if (!reconhecida) return false;

            JSObject data = new JSObject();
            data.put("action", currentAction);
            data.put("value", nativeInput.getText().toString());
            notifyListeners("editorAction", data);
            return true;
        });
    }

    private int imeAction(String action) {
        if ("next".equals(action)) return EditorInfo.IME_ACTION_NEXT;
        if ("send".equals(action)) return EditorInfo.IME_ACTION_SEND;
        return EditorInfo.IME_ACTION_DONE;
    }

    @PluginMethod
    public void focusInput(PluginCall call) {
        final String value = call.getString("value", "");
        final Integer startObj = call.getInt("selectionStart", value.length());
        final Integer endObj = call.getInt("selectionEnd", value.length());
        final String action = call.getString("action", "done");

        getActivity().runOnUiThread(() -> {
            try {
                ensureInput();
                currentAction = action == null ? "done" : action;

                // Campo de texto livre: solicita explicitamente autocorreção e
                // não usa TYPE_TEXT_FLAG_AUTO_COMPLETE nem NO_SUGGESTIONS.
                nativeInput.setInputType(
                    InputType.TYPE_CLASS_TEXT |
                    InputType.TYPE_TEXT_VARIATION_NORMAL |
                    InputType.TYPE_TEXT_FLAG_AUTO_CORRECT |
                    InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
                );
                nativeInput.setImeOptions(imeAction(currentAction) | EditorInfo.IME_FLAG_NO_EXTRACT_UI);

                internalChange = true;
                nativeInput.setText(value == null ? "" : value);
                int len = nativeInput.length();
                int start = Math.max(0, Math.min(startObj == null ? len : startObj, len));
                int end = Math.max(start, Math.min(endObj == null ? start : endObj, len));
                nativeInput.setSelection(start, end);
                internalChange = false;

                nativeInput.requestFocus();
                InputMethodManager imm = (InputMethodManager) getActivity().getSystemService(Context.INPUT_METHOD_SERVICE);
                if (imm != null) {
                    imm.restartInput(nativeInput);
                    nativeInput.postDelayed(() -> imm.showSoftInput(nativeInput, InputMethodManager.SHOW_IMPLICIT), 60);
                }

                call.resolve();
            } catch (Exception e) {
                internalChange = false;
                call.reject("Não foi possível ativar a entrada nativa.", e);
            }
        });
    }

    @PluginMethod
    public void hideInput(PluginCall call) {
        getActivity().runOnUiThread(() -> {
            try {
                if (nativeInput != null) {
                    InputMethodManager imm = (InputMethodManager) getActivity().getSystemService(Context.INPUT_METHOD_SERVICE);
                    if (imm != null) imm.hideSoftInputFromWindow(nativeInput.getWindowToken(), 0);
                    nativeInput.clearFocus();
                }
                call.resolve();
            } catch (Exception e) {
                call.reject("Não foi possível ocultar a entrada nativa.", e);
            }
        });
    }
}
'''


def patch_web():
    if not ROOT.exists():
        raise SystemExit('native/www não encontrado.')

    (ROOT / 'ime-nativo-real-v3827.js').write_text(WEB_JS, encoding='utf-8')
    (ROOT / 'ime-nativo-real-v3827.css').write_text(WEB_CSS, encoding='utf-8')

    alteradas = 0
    for nome in ('assistente-chat-v384.html', 'cadastro.html'):
        pagina = ROOT / nome
        if not pagina.exists():
            raise SystemExit(f'Página não encontrada: {nome}')
        texto = pagina.read_text(encoding='utf-8')

        if 'ime-nativo-real-v3827.css' not in texto:
            if '</head>' not in texto:
                raise SystemExit(f'</head> ausente em {nome}')
            texto = texto.replace('</head>', '    <link rel="stylesheet" href="ime-nativo-real-v3827.css?v=3827">\n</head>', 1)

        if 'ime-nativo-real-v3827.js' not in texto:
            if '</body>' not in texto:
                raise SystemExit(f'</body> ausente em {nome}')
            texto = texto.replace('</body>', '    <script src="ime-nativo-real-v3827.js?v=3827"></script>\n</body>', 1)

        pagina.write_text(texto, encoding='utf-8')
        alteradas += 1

    final = (ROOT / 'ime-nativo-real-v3827.js').read_text(encoding='utf-8')
    for marca in ('NativeIme', 'focusInput', 'textChanged', 'editorAction', 'seed-ime-nativo-ativo-v3827'):
        if marca not in final and marca != 'seed-ime-nativo-ativo-v3827':
            raise SystemExit(f'Marca web ausente: {marca}')

    print(f'Ponte web da entrada nativa aplicada em {alteradas} telas.')


def patch_android():
    android = Path('native/android')
    if not android.exists():
        raise SystemExit('native/android não encontrado. Execute após npx cap add/sync.')

    mains = list(android.glob('app/src/main/java/**/MainActivity.java'))
    if len(mains) != 1:
        raise SystemExit(f'Esperado 1 MainActivity.java; encontrados: {len(mains)}')

    main = mains[0]
    texto = main.read_text(encoding='utf-8')
    m = re.search(r'^\s*package\s+([\w.]+)\s*;', texto, flags=re.M)
    if not m:
        raise SystemExit('Package do MainActivity não encontrado.')
    package = m.group(1)
    if package != 'br.com.seedcontrol.app':
        raise SystemExit(f'Package inesperado: {package}')

    plugin_path = main.parent / 'NativeImePlugin.java'
    plugin_path.write_text(JAVA_PLUGIN, encoding='utf-8')

    main.write_text(
        '''package br.com.seedcontrol.app;\n\n'''
        '''import android.os.Bundle;\n'''
        '''import com.getcapacitor.BridgeActivity;\n\n'''
        '''public class MainActivity extends BridgeActivity {\n'''
        '''    @Override\n'''
        '''    public void onCreate(Bundle savedInstanceState) {\n'''
        '''        registerPlugin(NativeImePlugin.class);\n'''
        '''        super.onCreate(savedInstanceState);\n'''
        '''    }\n'''
        '''}\n''',
        encoding='utf-8'
    )

    if 'TYPE_TEXT_FLAG_AUTO_CORRECT' not in plugin_path.read_text(encoding='utf-8'):
        raise SystemExit('AUTO_CORRECT ausente no plugin nativo.')
    if 'TYPE_TEXT_FLAG_NO_SUGGESTIONS' in plugin_path.read_text(encoding='utf-8'):
        raise SystemExit('NO_SUGGESTIONS não pode existir no plugin nativo.')
    if 'registerPlugin(NativeImePlugin.class)' not in main.read_text(encoding='utf-8'):
        raise SystemExit('NativeImePlugin não registrado no MainActivity.')

    print('NativeImePlugin criado e registrado com AUTO_CORRECT e sem NO_SUGGESTIONS.')


if MODE == '--web':
    patch_web()
elif MODE == '--android':
    patch_android()
else:
    raise SystemExit('Use --web ou --android')
