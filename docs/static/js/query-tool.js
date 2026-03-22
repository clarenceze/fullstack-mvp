(function () {
	"use strict";

	const API_BASE = "https://api.clarenceze.com/api";

	const loadBtn = document.getElementById("loadData");
	const genBtn = document.getElementById("generateSQL");
	const userQuery = document.getElementById("userQuery");
	const llmResult = document.getElementById("llmResult");
	const sqlOutput = document.getElementById("sqlOutput");
	const descOutput = document.getElementById("descOutput");
	const gamesTable = document.getElementById("gamesTable");
	const statusEl = document.getElementById("queryToolStatus");

	if (!loadBtn || !genBtn || !gamesTable || !statusEl) return;

	const loadLabel = "Load Top 10";
	const genLabel = "Run query";

	function setStatus(msg, isError) {
		if (!msg) {
			statusEl.textContent = "";
			statusEl.hidden = true;
			statusEl.classList.remove("query-tool-status--error");
			return;
		}
		statusEl.textContent = msg;
		statusEl.hidden = false;
		statusEl.classList.toggle("query-tool-status--error", !!isError);
	}

	function setLoading(loading, which) {
		if (which === "load" || which === "both") {
			loadBtn.disabled = loading;
			loadBtn.textContent = loading ? "Loading…" : loadLabel;
		}
		if (which === "llm" || which === "both") {
			genBtn.disabled = loading;
			genBtn.textContent = loading ? "Querying…" : genLabel;
		}
	}

	async function parseHttpError(response) {
		const text = await response.text();
		try {
			const j = JSON.parse(text);
			if (j.detail !== undefined) {
				if (typeof j.detail === "string") return j.detail;
				if (Array.isArray(j.detail))
					return j.detail.map(function (d) {
						return d.msg || JSON.stringify(d);
					}).join("; ");
			}
		} catch (_) {}
		return text || response.statusText || "Request failed";
	}

	/** Browsers often surface CORS / offline as TypeError: Failed to fetch */
	function formatFetchError(err, prefix) {
		var m = err && err.message ? err.message : String(err);
		if (/failed to fetch|networkerror|load failed/i.test(m)) {
			m +=
				" (often CORS: allow this origin on the API, e.g. http://localhost:<port>; redeploy after changes.)";
		}
		return prefix ? prefix + m : m;
	}

	function setCellText(td, value) {
		td.textContent = value == null ? "" : String(value);
	}

	function renderTableFromColumns(columns, rows) {
		const thead = gamesTable.querySelector("thead");
		const tbody = gamesTable.querySelector("tbody");
		thead.innerHTML = "";
		tbody.innerHTML = "";

		const headerRow = document.createElement("tr");
		columns.forEach(function (col) {
			const th = document.createElement("th");
			th.textContent = col;
			headerRow.appendChild(th);
		});
		thead.appendChild(headerRow);

		rows.forEach(function (row) {
			const tr = document.createElement("tr");
			row.forEach(function (cell, idx) {
				const td = document.createElement("td");
				setCellText(td, cell);
				const colName = (columns[idx] || "").toLowerCase();
				if (
					colName.includes("sales") ||
					colName.includes("sale") ||
					colName.includes("global")
				) {
					td.classList.add("numeric");
				}
				tr.appendChild(td);
			});
			tbody.appendChild(tr);
		});

		gamesTable.hidden = false;
	}

	function renderTop10(data) {
		const thead = gamesTable.querySelector("thead");
		const tbody = gamesTable.querySelector("tbody");
		thead.innerHTML = "";
		tbody.innerHTML = "";

		const hr = document.createElement("tr");
		const th1 = document.createElement("th");
		th1.textContent = "Name";
		const th2 = document.createElement("th");
		th2.textContent = "Global Sales (millions)";
		hr.appendChild(th1);
		hr.appendChild(th2);
		thead.appendChild(hr);

		data.forEach(function (row) {
			const tr = document.createElement("tr");
			const td1 = document.createElement("td");
			const td2 = document.createElement("td");
			td1.textContent = row.name != null ? String(row.name) : "";
			td2.textContent = row.global_sales != null ? String(row.global_sales) : "";
			td2.classList.add("numeric");
			tr.appendChild(td1);
			tr.appendChild(td2);
			tbody.appendChild(tr);
		});

		gamesTable.hidden = false;
	}

	loadBtn.addEventListener("click", async function () {
		setStatus("");
		setLoading(true, "load");
		try {
			const response = await fetch(API_BASE + "/query");
			if (!response.ok) throw new Error(await parseHttpError(response));
			const data = await response.json();
			if (!Array.isArray(data)) {
				if (data && data.error) throw new Error(String(data.error));
				throw new Error("Invalid response format");
			}
			if (llmResult) llmResult.hidden = true;
			renderTop10(data);
		} catch (err) {
			setStatus(formatFetchError(err), true);
		} finally {
			setLoading(false, "load");
		}
	});

	genBtn.addEventListener("click", async function () {
		const question = userQuery ? userQuery.value.trim() : "";
		if (!question) {
			setStatus("Enter a question first.", true);
			return;
		}

		setStatus("");
		setLoading(true, "llm");
		try {
			const url =
				API_BASE +
				"/query_llm?question=" +
				encodeURIComponent(question);
			const response = await fetch(url);
			if (!response.ok) throw new Error(await parseHttpError(response));
			const data = await response.json();

			if (llmResult && sqlOutput && descOutput) {
				llmResult.hidden = false;
				sqlOutput.textContent = data.sql || "⚠️ No SQL returned";
				descOutput.textContent = data.desc || "⚠️ No explanation from model";
			}

			const tbody = gamesTable.querySelector("tbody");
			const thead = gamesTable.querySelector("thead");
			tbody.innerHTML = "";
			thead.innerHTML = "";

			if (data.columns && data.data && data.data.length > 0) {
				renderTableFromColumns(data.columns, data.data);
			} else {
				gamesTable.hidden = true;
			}
		} catch (err) {
			setStatus(formatFetchError(err, "Query failed: "), true);
		} finally {
			setLoading(false, "llm");
		}
	});

	if (userQuery) {
		userQuery.addEventListener("keydown", function (e) {
			if (e.key === "Enter") {
				e.preventDefault();
				genBtn.click();
			}
		});
	}
})();
