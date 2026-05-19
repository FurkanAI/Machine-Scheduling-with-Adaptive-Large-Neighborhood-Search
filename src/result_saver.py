import json
from pathlib import Path
from datetime import datetime, timezone

class ResultSaver:

    def __init__(self, file_name: str = "default_test", output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now(timezone.utc).isoformat().replace(':', '-')
        self.file_name = f"{file_name}_{self.timestamp}"

    def save(self, alns, gurobi_refinement, config, problem, extra_meta: dict = None):

        meta = {
            "experiment_name": config.experiment.name,
            "problem_path": problem.instance_path,
            "timestamp": self.timestamp
        }

        if extra_meta:
            meta.update(extra_meta)

        problem_data = {
            "total_jobs": problem.total_jobs,
            "total_machines": problem.total_machines,
            "processing_times": problem.processing_times.tolist(),
            "setup_times": problem.setup_times.tolist()
        }
        
        config_data = {
            "experiment": config.experiment.__dict__,
            "instance": config.instance.__dict__,
            "alns": config.alns.__dict__,
            "gurobi_refinement": config.gurobi_refinement.__dict__,
            "objective": {
                "weights": config.objective.weights.__dict__
            },
            "random": config.random.__dict__
        }

        alns_data = {
            "assignment_matrix": alns.best_solution.assignment_matrix.tolist(),
            "used_server_count": int(alns.best_solution.used_server_count),
            "used_machine_count": int(alns.best_solution.used_machine_count),
            "completion_times": alns.best_solution.completion_times.tolist(),
            "cost": alns.best_solution.cost,
            "runtime": alns.runtime
        }

        if gurobi_refinement.has_solution():
            gurobi_data = {
                "completion_times": gurobi_refinement.best_solution.completion_times.tolist(),
                "cost": gurobi_refinement.best_solution.cost,
                "runtime": gurobi_refinement.runtime,
                "status": gurobi_refinement.status,
                "solution_count": gurobi_refinement.solution_count,
                "optimization_time": gurobi_refinement.optimization_time,
                "constraint_time": gurobi_refinement.constraint_time,
                "variable_assignment_time": gurobi_refinement.variable_assignment_time
            }
            result = {
            "meta": meta,
            #"problem": problem_data,
            "config": config_data,
            "alns": alns_data,
            "gurobi_refinement": gurobi_data
        }
        else:
            result = {
                "meta": meta,
                #"problem": problem_data,
                "config": config_data,
                "alns": alns_data,
            }

        file_name = f"{self.file_name}.json"
        file_path = self.output_dir / file_name

        with open(file_path, "w") as f:
            json.dump(result, f, indent=4)

        return str(file_path)
    

    def generate_gantt(self, solution, problem):

        job_ids = solution.assignment_matrix[0]
        machine_ids = solution.assignment_matrix[1]
        num_jobs = problem.total_jobs
        num_machines = problem.total_machines
        
        machine_schedules = {m: [] for m in range(num_machines)}
        
        critical_times = set([0])  # Başlangıç noktası
        
        for idx in range(num_jobs):
            j_id = job_ids[idx]
            m_id = machine_ids[idx]
            j_idx = j_id - 1
            m_idx = m_id - 1
            p_time = problem.processing_times[j_idx][m_idx]
            s_time = problem.setup_times[j_idx][m_idx]
            c_time = solution.completion_times[j_idx]
            
            start_time = c_time - p_time - s_time
            setup_end_time = start_time + s_time
            
            machine_schedules[m_idx].append({
                'job_display_id': j_id,
                'start': start_time,
                'setup_end': setup_end_time,
                'end': c_time,
                'p_time': p_time,
                's_time': s_time
            })
            

            critical_times.add(start_time)
            critical_times.add(setup_end_time)
            critical_times.add(c_time)    
            
        sorted_critical_times = sorted(list(critical_times))
        max_time = sorted_critical_times[-1] if sorted_critical_times else 100
        min_diff_time = min(sorted_critical_times[i+1] - sorted_critical_times[i] for i in range(len(sorted_critical_times)-1)) if len(sorted_critical_times) > 1 else 10
        
    
        margin_left = 90
        margin_right = 50
        margin_top = 90       
        margin_bottom = 80    
        
        row_height = 100   
        bar_height = 60   
        graph_width = 40 * max_time // min_diff_time
        graph_height = num_machines * row_height
        
        svg_width = graph_width + margin_left + margin_right
        svg_height = graph_height + margin_top + margin_bottom
        scale_x = graph_width / max_time
        
        colors = ["#3498db", "#2ecc71", "#9b59b6", "#f1c40f", "#e67e22", "#e74c3c", "#1abc9c", "#34495e", "#fdcb6e", "#6c5ce7"]
        
        svg = []
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">')
        svg.append('<style>')
        svg.append('  .title { font-family: "Segoe UI", sans-serif; font-size: 22px; font-weight: bold; fill: #2c3e50; }')
        svg.append('  .axis-label { font-family: "Segoe UI", sans-serif; font-size: 13px; fill: #2c3e50; font-weight: bold; }')
        svg.append('  .tick-text { font-family: "Segoe UI", sans-serif; font-size: 10px; fill: #2c3e50; font-weight: bold; }')
        svg.append('  .bar-main-text { font-family: "Segoe UI", sans-serif; font-size: 12px; font-weight: bold; fill: white; text-anchor: middle; }')
        svg.append('  .bar-sub-text { font-family: "Segoe UI", sans-serif; font-size: 10px; fill: rgba(255,255,255,0.9); text-anchor: middle; }')
        svg.append('  .setup-main-text { font-family: "Segoe UI", sans-serif; font-size: 11px; font-weight: bold; fill: #57606f; text-anchor: middle; }')
        svg.append('  .setup-sub-text { font-family: "Segoe UI", sans-serif; font-size: 10px; fill: #747d8c; text-anchor: middle; }')
        svg.append('  .legend-text { font-family: "Segoe UI", sans-serif; font-size: 12px; font-weight: bold; fill: #2c3e50; }')
        svg.append('  .critical-line { stroke: #b2bec3; stroke-width: 0.7; stroke-dasharray: 2,4; }')
        svg.append('  .machine-line { stroke: #f1f2f6; stroke-width: 2; }')
        svg.append('<title>Strict Gantt Chart</title></style>')
        
        svg.append('<defs>')
        svg.append('  <pattern id="diagonal-stripe" width="8" height="8" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">')
        svg.append('    <line x1="0" y1="0" x2="0" y2="8" style="stroke:#ced6e0; stroke-width:3" />')
        svg.append('    <line x1="0" y1="0" x2="0" y2="8" style="stroke:#f8f9fa; stroke-width:5" transform="translate(4,0)" />')
        svg.append('  </pattern>')
        svg.append('--></defs>')
        
        svg.append(f'<rect width="{svg_width}" height="{svg_height}" fill="#ffffff"/>')
        svg.append(f'<text x="{margin_left}" y="42" text-anchor="start" class="title">Production Schedule Gantt Chart</text>')
        

        legend_x_start = svg_width - margin_right - 340
        svg.append(f'  <rect x="{legend_x_start}" y="25" width="40" height="22" fill="url(#diagonal-stripe)" stroke="#95a5a6" stroke-width="1" rx="2"/>')
        svg.append(f'  <text x="{legend_x_start + 50}" y="40" class="legend-text">Setup Operation</text>')
        svg.append(f'  <rect x="{legend_x_start + 180}" y="25" width="40" height="22" fill="#3498db" stroke="#2c3e50" stroke-width="0.5" rx="3"/>')
        svg.append(f'  <text x="{legend_x_start + 230}" y="40" class="legend-text">Processing Operation</text>')
        
        last_y_state = 0  
        last_x_pos = -999
        
        for t_val in sorted_critical_times:
            x_pos = margin_left + (t_val * scale_x)
            
            svg.append(f'  <line x1="{x_pos}" y1="{margin_top}" x2="{x_pos}" y2="{margin_top + graph_height}" class="critical-line" />')
            
            if x_pos - last_x_pos < 40:
                y_offset = (margin_top + graph_height + 31) if last_y_state == 0 else (margin_top + graph_height + 18)
                last_y_state = 1 if last_y_state == 0 else 0
            else:
                y_offset = margin_top + graph_height + 18
                last_y_state = 0
                
            svg.append(f'  <text x="{x_pos}" y="{y_offset}" text-anchor="middle" class="tick-text">{t_val}</text>')
            last_x_pos = x_pos
        
        svg.append(f'<text x="{margin_left + graph_width/2}" y="{svg_height - 15}" text-anchor="middle" class="axis-label">Time</text>')
        
        for m in range(num_machines):
            y_row_center = margin_top + (m * row_height) + (row_height / 2)
            y_bar_top = y_row_center - (bar_height / 2)
            
            svg.append(f'  <text x="{margin_left - 15}" y="{y_row_center + 5}" text-anchor="end" class="axis-label">Machine {m+1}</text>')
            svg.append(f'  <line x1="{margin_left}" y1="{y_row_center + bar_height/2 + 12}" x2="{margin_left + graph_width}" y2="{y_row_center + bar_height/2 + 12}" class="machine-line"/>')
            
            for task in machine_schedules[m]:
                j_num = task['job_display_id']
                s_x = margin_left + (task['start'] * scale_x)
                se_x = margin_left + (task['setup_end'] * scale_x)
                e_x = margin_left + (task['end'] * scale_x)
                
                w_setup = se_x - s_x
                w_proc = e_x - se_x
                color = colors[(j_num - 1) % len(colors)]
                
                if w_setup > 0:
                    svg.append(f'  <rect x="{s_x}" y="{y_bar_top}" width="{w_setup}" height="{bar_height}" fill="url(#diagonal-stripe)" stroke="#95a5a6" stroke-width="0.8" rx="2"/>')
                    if w_setup > 25:
                        svg.append(f'  <text x="{s_x + w_setup/2}" y="{y_row_center - 2}" class="setup-main-text">J{j_num}</text>')
                        svg.append(f'  <text x="{s_x + w_setup/2}" y="{y_row_center + 11}" class="setup-sub-text">d={task["s_time"]}</text>')
                
                if w_proc > 0:
                    svg.append(f'  <rect x="{se_x}" y="{y_bar_top}" width="{w_proc}" height="{bar_height}" fill="{color}" rx="4" stroke="#2c3e50" stroke-width="0.5" />')
                    if w_proc > 35:
                        svg.append(f'  <text x="{se_x + w_proc/2}" y="{y_row_center - 2}" class="bar-main-text">J{j_num}</text>')
                        svg.append(f'  <text x="{se_x + w_proc/2}" y="{y_row_center + 11}" class="bar-sub-text">d={task["p_time"]}</text>')
                    else:
                        svg.append(f'  <text x="{se_x + w_proc/2}" y="{y_row_center + 4}" class="bar-main-text">J{j_num}</text>')

        svg.append(f'  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + graph_height}" stroke="#2c3e50" stroke-width="2" />')
        svg.append(f'  <line x1="{margin_left}" y1="{margin_top + graph_height}" x2="{margin_left + graph_width}" y2="{margin_top + graph_height}" stroke="#2c3e50" stroke-width="2" />')
        svg.append('</svg>')
        
        svg_content = "\n".join(svg).replace('--></defs>', '</defs>')
        
        file_name = f"{self.file_name}.svg"
        file_path = self.output_dir / file_name
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
