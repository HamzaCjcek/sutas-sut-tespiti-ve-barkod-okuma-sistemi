document.addEventListener("DOMContentLoaded", function () {

    // ============================================================
    // MODEL AYARLARI
    // ============================================================

    const MODEL_CONFIG = {
        milk: {
            name: "Süt Modeli",
            buttonText: "Süt modelini çalıştır",
            endpoint: "/Home/TestPythonAnalyze"
        },

        yogurt: {
            name: "Yoğurt Modeli",
            buttonText: "Yoğurt modelini çalıştır",
            endpoint: null
        }
    };


    // ============================================================
    // STATE
    // ============================================================

    const state = {
        activeModel: "milk",
        currentFile: null,
        imageObjectUrl: "",
        lastResult: null,
        lastDetections: []
    };


    // ============================================================
    // HTML ELEMENTLERİ
    // ============================================================

    const elements = {

        modelButtons:
            [...document.querySelectorAll(".model-card")],

        selectedModelName:
            document.getElementById("selectedModelName"),

        selectedModelIcon:
            document.getElementById("selectedModelIcon"),

        analyzeButton:
            document.getElementById("analyzeButton"),

        fileInput:
            document.getElementById("fileInput"),

        chooseImageButton:
            document.getElementById("chooseImageButton"),

        changeImageButton:
            document.getElementById("changeImageButton"),

        dropzone:
            document.getElementById("dropzone"),

        previewStage:
            document.getElementById("previewStage"),

        previewImage:
            document.getElementById("previewImage"),

        boxesLayer:
            document.getElementById("boxesLayer"),

        scanOverlay:
            document.getElementById("scanOverlay"),

        fileStrip:
            document.getElementById("fileStrip"),

        fileName:
            document.getElementById("fileName"),

        confidenceRange:
            document.getElementById("confidenceRange"),

        confidenceValue:
            document.getElementById("confidenceValue"),

        formMessage:
            document.getElementById("formMessage"),

        resultsSection:
            document.getElementById("sonuclar"),

        evaluationSection:
            document.getElementById("degerlendirme"),

        downloadButton:
            document.getElementById("downloadButton"),

        demoButton:
            document.getElementById("demoButton"),

        toast:
            document.getElementById("toast")
    };


    // ============================================================
    // SABİT CONFIDENCE
    // Python tarafı PRODUCT_CONF = 0.35
    // ============================================================

    if (elements.confidenceRange) {

        elements.confidenceRange.value = 35;
        elements.confidenceRange.disabled = true;

    }

    if (elements.confidenceValue) {

        elements.confidenceValue.textContent = "%35";

    }


    // ============================================================
    // DEMO BUTONUNU GİZLE
    // Artık gerçek API kullanıyoruz.
    // ============================================================

    if (elements.demoButton) {

        elements.demoButton.classList.add("hidden");

    }


    // ============================================================
    // MODEL SEÇİMİ
    // ============================================================

    function setActiveModel(modelKey) {

        state.activeModel = modelKey;

        const config =
            MODEL_CONFIG[modelKey];


        elements.modelButtons.forEach(function (button) {

            const selected =
                button.dataset.model === modelKey;

            button.classList.toggle(
                "selected",
                selected
            );

            button.setAttribute(
                "aria-pressed",
                String(selected)
            );


            const status =
                button.querySelector(
                    ".model-card-meta b"
                );

            if (status) {

                status.textContent =
                    selected
                        ? "Aktif"
                        : "Seç";

            }

        });


        if (elements.selectedModelName) {

            elements.selectedModelName.textContent =
                config.name;

        }


        if (elements.selectedModelIcon) {

            elements.selectedModelIcon.className =
                `product-icon ${modelKey} mini`;

        }


        const buttonText =
            elements.analyzeButton
                ?.querySelector("b");

        if (buttonText) {

            buttonText.textContent =
                config.buttonText;

        }


        hideResults();

        clearMessage();

    }


    // ============================================================
    // DOSYA SEÇİCİ
    // ============================================================

    function openFilePicker(event) {

        event?.stopPropagation();

        elements.fileInput?.click();

    }


    // ============================================================
    // DOSYA KONTROLÜ
    // ============================================================

    function validateAndLoadFile(file) {

        if (!file) {
            return;
        }


        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ];


        if (!allowedTypes.includes(file.type)) {

            showMessage(
                "Lütfen JPG, PNG veya WEBP biçiminde bir görsel seçin."
            );

            return;

        }


        const maximumSize =
            10 * 1024 * 1024;


        if (file.size > maximumSize) {

            showMessage(
                "Görsel boyutu en fazla 10 MB olabilir."
            );

            return;

        }


        if (state.imageObjectUrl) {

            URL.revokeObjectURL(
                state.imageObjectUrl
            );

        }


        state.currentFile = file;

        state.imageObjectUrl =
            URL.createObjectURL(file);


        loadPreview(
            state.imageObjectUrl,
            file.name
        );

    }


    // ============================================================
    // GÖRSEL ÖNİZLEME
    // ============================================================

    function loadPreview(
        source,
        fileName
    ) {

        elements.previewImage.src =
            source;


        elements.previewStage
            .classList
            .remove("hidden");


        elements.dropzone
            .classList
            .add("hidden");


        elements.fileStrip
            .classList
            .remove("hidden");


        elements.changeImageButton
            .classList
            .remove("hidden");


        elements.fileName.textContent =
            fileName;


        if (elements.boxesLayer) {

            elements.boxesLayer.innerHTML =
                "";

        }


        hideResults();

        clearMessage();

    }


    // ============================================================
    // ANALİZ
    // ============================================================

    async function runAnalysis() {

        // --------------------------------------------------------
        // MODEL KONTROLÜ
        // --------------------------------------------------------

        const config =
            MODEL_CONFIG[state.activeModel];


        if (!config.endpoint) {

            showMessage(
                "Yoğurt modeli henüz API'ye bağlanmadı."
            );

            return;

        }


        // --------------------------------------------------------
        // GÖRSEL KONTROLÜ
        // --------------------------------------------------------

        if (!state.currentFile) {

            showMessage(
                "Analize başlamak için bir raf görseli yükleyin."
            );

            return;

        }


        setLoading(true);

        clearMessage();


        const startTime =
            performance.now();


        try {

            const data =
                await callModelApi(
                    state.currentFile,
                    config.endpoint
                );


            const endTime =
                performance.now();


            const processingMs =
                Math.round(
                    endTime - startTime
                );


            const result =
                normalizeApiResult(
                    data,
                    processingMs
                );


            state.lastResult =
                result;

            state.lastDetections =
                result.detections;


            // ====================================================
            // Python zaten kutuları çizdi.
            // annotatedImage doğrudan ekranda gösteriliyor.
            // ====================================================

            if (result.annotatedImage) {

                elements.previewImage.src =
                    "data:image/jpeg;base64,"
                    +
                    result.annotatedImage;

            }


            if (elements.boxesLayer) {

                elements.boxesLayer.innerHTML =
                    "";

            }


            renderDashboard(
                result,
                result.detections
            );


            elements.resultsSection
                .classList
                .remove("hidden");


            elements.evaluationSection
                .classList
                .remove("hidden");


            elements.resultsSection
                .scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });


            showToast(
                "Analiz başarıyla tamamlandı"
            );

        }
        catch (error) {

            console.error(
                "Analiz hatası:",
                error
            );


            showMessage(
                error.message ||
                "Analiz sırasında bir hata oluştu."
            );

        }
        finally {

            setLoading(false);

        }

    }


    // ============================================================
    // ASP.NET CORE API ÇAĞRISI
    //
    // Browser
    //      ↓
    // /Home/TestPythonAnalyze
    //      ↓
    // PythonApiService
    //      ↓
    // FastAPI
    // ============================================================

    async function callModelApi(
        file,
        endpoint
    ) {

        const formData =
            new FormData();


        formData.append(
            "image",
            file
        );


        const response =
            await fetch(
                endpoint,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();


            throw new Error(
                errorText ||
                `Sunucu ${response.status} kodunu döndürdü.`
            );

        }


        return await response.json();

    }


    // ============================================================
    // PYTHON JSON -> WEB FORMAT
    //
    // Python:
    //
    // products:
    // [
    //   {
    //      className: "sutas",
    //      confidence: 0.90,
    //      brandScore: 0.88,
    //      box: {...}
    //   }
    // ]
    // ============================================================

    function normalizeApiResult(
        data,
        processingMs
    ) {

        if (!data.success) {

            throw new Error(
                "Model analizi başarısız oldu."
            );

        }


        const products =
            Array.isArray(data.products)
                ? data.products
                : [];


        const detections =
            products.map(function (product) {

                const isSutasProduct =
                    product.className ===
                    "sutas";


                return {

                    label:
                        isSutasProduct
                            ? "Sütaş Süt"
                            : "Rakip Süt",

                    brand:
                        isSutasProduct
                            ? "Sütaş"
                            : "Rakip",

                    confidence:
                        Number(
                            product.confidence
                            || 0
                        ),

                    brandScore:
                        Number(
                            product.brandScore
                            || 0
                        ),

                    box:
                        product.box || null

                };

            });


        return {

            model:
                state.activeModel,

            detections:
                detections,

            counts:
                data.counts || {
                    total: detections.length,
                    sutas: 0,
                    other: 0
                },

            thresholds:
                data.thresholds || {},

            annotatedImage:
                data.annotatedImage || "",

            processingMs:
                processingMs,

            generatedAt:
                new Date().toISOString()

        };

    }


    // ============================================================
    // DASHBOARD
    // ============================================================

    function renderDashboard(
        result,
        detections
    ) {

        const total =
            result.counts?.total
            ?? detections.length;


        const sutas =
            result.counts?.sutas
            ??
            detections.filter(
                item =>
                    item.brand === "Sütaş"
            ).length;


        const competitors =
            result.counts?.other
            ??
            total - sutas;


        const sutasShare =
            total
                ? Math.round(
                    (sutas / total) * 100
                )
                : 0;


        const competitorShare =
            total
                ? 100 - sutasShare
                : 0;


        const averageConfidence =
            total
                ? Math.round(
                    (
                        detections.reduce(
                            (
                                sum,
                                item
                            ) =>
                                sum
                                +
                                item.confidence,
                            0
                        )
                        /
                        total
                    )
                    *
                    100
                )
                : 0;


        const classCounts =
            countClasses(
                detections
            );


        setText(
            "totalCount",
            total
        );


        setText(
            "sutasCount",
            sutas
        );


        setText(
            "competitorCount",
            competitors
        );


        setText(
            "averageConfidence",
            `%${averageConfidence}`
        );


        setText(
            "sutasShareText",
            `Rafın %${sutasShare}'ı`
        );


        setText(
            "competitorShareText",
            `Rafın %${competitorShare}'ı`
        );


        setText(
            "processingTime",
            `${result.processingMs} ms işlem süresi`
        );


        setText(
            "resultModelBadge",
            MODEL_CONFIG[
                state.activeModel
            ].name
        );


        setText(
            "donutValue",
            `%${sutasShare}`
        );


        setText(
            "legendSutas",
            `${sutas} ürün`
        );


        setText(
            "legendCompetitors",
            `${competitors} ürün`
        );


        setText(
            "detectionListCount",
            `${total} kayıt`
        );


        drawShareChart(
            sutas,
            competitors
        );


        renderClassChart(
            classCounts
        );


        renderDetectionTable(
            detections
        );


        renderEvaluation({

            total,

            sutas,

            competitors,

            sutasShare,

            averageConfidence,

            classCounts

        });

    }


    // ============================================================
    // DONUT CHART
    // ============================================================

    function drawShareChart(
        sutas,
        competitors
    ) {

        const canvas =
            document.getElementById(
                "shareChart"
            );


        if (!canvas) {
            return;
        }


        const context =
            canvas.getContext("2d");


        const size =
            280;


        const dpr =
            window.devicePixelRatio || 1;


        canvas.width =
            size * dpr;

        canvas.height =
            size * dpr;


        context.setTransform(
            dpr,
            0,
            0,
            dpr,
            0,
            0
        );


        context.clearRect(
            0,
            0,
            size,
            size
        );


        const total =
            sutas + competitors;


        const sutasAngle =
            total
                ? (
                    sutas / total
                )
                *
                Math.PI
                *
                2
                : 0;


        const startAngle =
            -Math.PI / 2;


        context.lineWidth =
            26;

        context.lineCap =
            "butt";


        context.strokeStyle =
            "#e2e6e2";


        context.beginPath();

        context.arc(
            140,
            140,
            92,
            0,
            Math.PI * 2
        );

        context.stroke();


        if (sutasAngle > 0) {

            context.strokeStyle =
                "#d9202d";


            context.beginPath();


            context.arc(
                140,
                140,
                92,
                startAngle,
                startAngle
                +
                sutasAngle
            );


            context.stroke();

        }

    }


    // ============================================================
    // CLASS CHART
    // ============================================================

    function renderClassChart(
        classCounts
    ) {

        const container =
            document.getElementById(
                "classChart"
            );


        if (!container) {
            return;
        }


        container.innerHTML =
            "";


        const entries =
            Object.entries(
                classCounts
            );


        const maximum =
            Math.max(
                ...entries.map(
                    ([, count]) =>
                        count
                ),
                1
            );


        entries.forEach(
            function ([label, count]) {

                const row =
                    document.createElement(
                        "div"
                    );


                const competitor =
                    !isSutas(label);


                row.className =
                    "bar-row";


                row.innerHTML = `

                    <span class="bar-label">
                        ${escapeHtml(label)}
                    </span>

                    <span class="bar-track">

                        <i
                            class="bar-fill${competitor ? " competitor" : ""}"
                            style="width:${(count / maximum) * 100}%">
                        </i>

                    </span>

                    <b class="bar-value">
                        ${count}
                    </b>

                `;


                container.appendChild(
                    row
                );

            }
        );

    }


    // ============================================================
    // TABLO
    // ============================================================

    function renderDetectionTable(
        detections
    ) {

        const body =
            document.getElementById(
                "detectionsTable"
            );


        if (!body) {
            return;
        }


        body.innerHTML =
            "";


        detections.forEach(
            function (
                detection,
                index
            ) {

                const sutas =
                    detection.brand ===
                    "Sütaş";


                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

                    <td>
                        ${String(index + 1).padStart(2, "0")}
                    </td>

                    <td>
                        <b>
                            ${escapeHtml(detection.label)}
                        </b>
                    </td>

                    <td>

                        <span class="brand-tag ${sutas ? "sutas" : "competitor"}">

                            ${sutas ? "Sütaş" : "Rakip"}

                        </span>

                    </td>

                    <td>

                        <div class="confidence-cell">

                            <b>
                                %${Math.round(detection.confidence * 100)}
                            </b>

                            <span class="confidence-mini">

                                <i style="width:${Math.round(detection.confidence * 100)}%">
                                </i>

                            </span>

                        </div>

                    </td>

                    <td>
                        <span class="status-tag">
                            Geçerli
                        </span>
                    </td>

                `;


                body.appendChild(
                    row
                );

            }
        );

    }


    // ============================================================
    // GENEL DEĞERLENDİRME
    // ============================================================

    function renderEvaluation(
        metrics
    ) {

        const diversity =
            Object.keys(
                metrics.classCounts
            ).length;


        const diversityScore =
            Math.min(
                100,
                diversity * 20
            );


        const score =
            Math.round(

                metrics.sutasShare
                *
                0.45

                +

                metrics.averageConfidence
                *
                0.35

                +

                diversityScore
                *
                0.20

            );


        let scoreLabel;

        if (score >= 80) {

            scoreLabel =
                "Çok iyi";

        }
        else if (score >= 65) {

            scoreLabel =
                "İyi";

        }
        else if (score >= 45) {

            scoreLabel =
                "Geliştirilebilir";

        }
        else {

            scoreLabel =
                "Düşük";

        }


        setText(
            "scoreValue",
            score
        );


        setText(
            "scoreLabel",
            scoreLabel
        );


        const scoreRing =
            document.getElementById(
                "scoreRing"
            );


        if (scoreRing) {

            scoreRing.style.background =
                `conic-gradient(
                    #d9202d 0deg,
                    #d9202d ${score * 3.6}deg,
                    rgba(255,255,255,.09) ${score * 3.6}deg
                )`;

        }


        setText(
            "evaluationDate",
            new Date()
                .toLocaleDateString(
                    "tr-TR",
                    {
                        day: "numeric",
                        month: "long",
                        year: "numeric"
                    }
                )
        );


        let title;
        let summary;
        let recommendationTitle;
        let recommendation;
        let priority;


        if (metrics.total === 0) {

            title =
                "Ürün tespiti bulunamadı";

            summary =
                "Görsel üzerinde geçerli ürün tespiti bulunamadı.";

            recommendationTitle =
                "Görseli yeniden kontrol edin";

            recommendation =
                "Rafı önden ve daha net şekilde çekerek analizi tekrar deneyin.";

            priority =
                "Yüksek";

        }
        else if (
            metrics.sutasShare >= 60
        ) {

            title =
                "Sütaş raf görünürlüğü güçlü";

            summary =
                `Analiz edilen rafta Sütaş ürünleri %${metrics.sutasShare} paya sahip.`;

            recommendationTitle =
                "Mevcut görünürlüğü koruyun";

            recommendation =
                "Sütaş ürünlerinin raf görünürlüğünü mevcut seviyede koruyun.";

            priority =
                "Normal";

        }
        else if (
            metrics.sutasShare >= 40
        ) {

            title =
                "Raf payı dengeli seviyede";

            summary =
                `Sütaş raf payı %${metrics.sutasShare} seviyesinde.`;

            recommendationTitle =
                "Sütaş görünürlüğünü artırın";

            recommendation =
                "Sütaş ürünlerinin raf üzerindeki cephe sayısını artırabilirsiniz.";

            priority =
                "Orta";

        }
        else {

            title =
                "Rakip görünürlüğü yüksek";

            summary =
                `Sütaş ürünleri rafın %${metrics.sutasShare}'ını oluşturuyor.`;

            recommendationTitle =
                "Raf yerleşimini güçlendirin";

            recommendation =
                "Sütaş ürünleri için daha fazla raf alanı ayrılması önerilir.";

            priority =
                "Yüksek";

        }


        setText(
            "summaryTitle",
            title
        );


        setText(
            "summaryText",
            summary
        );


        setText(
            "recommendationTitle",
            recommendationTitle
        );


        setText(
            "recommendationText",
            recommendation
        );


        setText(
            "priorityBadge",
            priority
        );


        const insightList =
            document.getElementById(
                "insightList"
            );


        if (insightList) {

            const insights = [

                `${metrics.total} ürün tespit edildi.`,

                `Sütaş raf payı %${metrics.sutasShare}.`,

                `Ortalama model güveni %${metrics.averageConfidence}.`

            ];


            insightList.innerHTML =
                insights
                    .map(
                        item => `

                            <div class="insight-item">

                                <span>✓</span>

                                <p>
                                    ${escapeHtml(item)}
                                </p>

                            </div>

                        `
                    )
                    .join("");

        }

    }


    // ============================================================
    // JSON İNDİR
    // ============================================================

    function downloadResult() {

        if (!state.lastResult) {
            return;
        }


        const blob =
            new Blob(
                [
                    JSON.stringify(
                        state.lastResult,
                        null,
                        2
                    )
                ],
                {
                    type:
                        "application/json"
                }
            );


        const url =
            URL.createObjectURL(
                blob
            );


        const link =
            document.createElement(
                "a"
            );


        link.href =
            url;


        link.download =
            "sutas-raf-analiz-sonucu.json";


        link.click();


        URL.revokeObjectURL(
            url
        );


        showToast(
            "Sonuç dosyası indirildi"
        );

    }


    // ============================================================
    // YARDIMCI FONKSİYONLAR
    // ============================================================

    function countClasses(
        detections
    ) {

        return detections.reduce(
            function (
                counts,
                item
            ) {

                counts[item.label] =
                    (
                        counts[item.label]
                        || 0
                    )
                    +
                    1;


                return counts;

            },
            {}
        );

    }


    function isSutas(
        label
    ) {

        return String(label)
            .toLocaleLowerCase(
                "tr-TR"
            )
            .includes(
                "sütaş"
            );

    }


    function setLoading(
        loading
    ) {

        elements.analyzeButton.disabled =
            loading;


        elements.scanOverlay
            ?.classList
            .toggle(
                "hidden",
                !loading
            );


        const icon =
            elements.analyzeButton
                ?.querySelector("span");


        const text =
            elements.analyzeButton
                ?.querySelector("b");


        if (icon) {

            icon.textContent =
                loading
                    ? "◌"
                    : "→";

        }


        if (text) {

            text.textContent =
                loading
                    ? "Görsel analiz ediliyor…"
                    : MODEL_CONFIG[
                        state.activeModel
                    ].buttonText;

        }

    }


    function hideResults() {

        state.lastResult =
            null;

        state.lastDetections =
            [];


        elements.resultsSection
            ?.classList
            .add("hidden");


        elements.evaluationSection
            ?.classList
            .add("hidden");

    }


    function showMessage(
        message
    ) {

        if (!elements.formMessage) {
            return;
        }


        elements.formMessage.textContent =
            message;


        elements.formMessage
            .classList
            .remove("hidden");

    }


    function clearMessage() {

        if (!elements.formMessage) {
            return;
        }


        elements.formMessage.textContent =
            "";


        elements.formMessage
            .classList
            .add("hidden");

    }


    function showToast(
        message
    ) {

        if (!elements.toast) {

            console.log(message);

            return;

        }


        elements.toast.textContent =
            message;


        elements.toast
            .classList
            .add("show");


        clearTimeout(
            showToast.timeout
        );


        showToast.timeout =
            setTimeout(
                function () {

                    elements.toast
                        .classList
                        .remove("show");

                },
                2600
            );

    }


    function setText(
        id,
        value
    ) {

        const element =
            document.getElementById(id);


        if (element) {

            element.textContent =
                value;

        }

    }


    function escapeHtml(
        value
    ) {

        return String(value)

            .replaceAll(
                "&",
                "&amp;"
            )

            .replaceAll(
                "<",
                "&lt;"
            )

            .replaceAll(
                ">",
                "&gt;"
            )

            .replaceAll(
                '"',
                "&quot;"
            )

            .replaceAll(
                "'",
                "&#039;"
            );

    }


    // ============================================================
    // EVENTLER
    // ============================================================

    elements.modelButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    setActiveModel(
                        button.dataset.model
                    );

                }
            );

        }
    );


    elements.chooseImageButton
        ?.addEventListener(
            "click",
            openFilePicker
        );


    elements.changeImageButton
        ?.addEventListener(
            "click",
            openFilePicker
        );


    elements.fileInput
        ?.addEventListener(
            "change",
            function (event) {

                validateAndLoadFile(
                    event.target.files?.[0]
                );

            }
        );


    elements.dropzone
        ?.addEventListener(
            "click",
            openFilePicker
        );


    elements.dropzone
        ?.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter"
                    ||
                    event.key === " "
                ) {

                    openFilePicker(
                        event
                    );

                }

            }
        );


    elements.dropzone
        ?.addEventListener(
            "dragover",
            function (event) {

                event.preventDefault();


                elements.dropzone
                    .classList
                    .add("dragging");

            }
        );


    elements.dropzone
        ?.addEventListener(
            "dragleave",
            function () {

                elements.dropzone
                    .classList
                    .remove("dragging");

            }
        );


    elements.dropzone
        ?.addEventListener(
            "drop",
            function (event) {

                event.preventDefault();


                elements.dropzone
                    .classList
                    .remove("dragging");


                const file =
                    event.dataTransfer
                        ?.files?.[0];


                validateAndLoadFile(
                    file
                );

            }
        );


    elements.analyzeButton
        ?.addEventListener(
            "click",
            runAnalysis
        );


    elements.downloadButton
        ?.addEventListener(
            "click",
            downloadResult
        );


    // ============================================================
    // BAŞLANGIÇ
    // ============================================================

    setActiveModel("milk");

});